data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

locals {
  public_subnets  = { for idx, cidr in var.public_subnet_cidrs : idx => cidr }
  private_subnets = { for idx, cidr in var.private_subnet_cidrs : idx => cidr }
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.environment}-vpc"
  }
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "${var.environment}-igw"
  }
}

resource "aws_subnet" "public" {
  for_each = local.public_subnets

  vpc_id            = aws_vpc.main.id
  cidr_block        = each.value
  availability_zone = data.aws_availability_zones.available.names[each.key]
  map_public_ip_on_launch = true
  tags = {
    Name = "${var.environment}-public-${each.key}"
  }
}

resource "aws_subnet" "private" {
  for_each = local.private_subnets

  vpc_id            = aws_vpc.main.id
  cidr_block        = each.value
  availability_zone = data.aws_availability_zones.available.names[each.key]
  tags = {
    Name = "${var.environment}-private-${each.key}"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
  tags = {
    Name = "${var.environment}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  for_each = aws_subnet.public
  subnet_id      = each.value.id
  route_table_id = aws_route_table.public.id
}

resource "aws_eip" "nat" {
  count = length(aws_subnet.public)
  depends_on = [aws_internet_gateway.gw]
}

resource "aws_nat_gateway" "nat" {
  count         = length(aws_subnet.public)
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = element([for s in aws_subnet.public : s.id], count.index)
  tags = {
    Name = "${var.environment}-nat-${count.index}"
  }
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat[0].id
  }
  tags = {
    Name = "${var.environment}-private-rt"
  }
}

resource "aws_route_table_association" "private" {
  for_each = aws_subnet.private
  subnet_id      = each.value.id
  route_table_id = aws_route_table.private.id
}

resource "aws_ecr_repository" "backend" {
  name = "servicenow-support-assistant-backend"
  image_tag_mutability = "MUTABLE"
}

resource "aws_s3_bucket" "frontend" {
  bucket = var.frontend_bucket_name != "" ? var.frontend_bucket_name : "${var.environment}-support-assistant-frontend-${data.aws_caller_identity.current.account_id}"
  acl    = "private"
  force_destroy = true

  tags = {
    Name = "${var.environment}-frontend"
  }
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_cloudfront_origin_access_identity" "frontend" {
  comment = "Access identity for ${var.environment} frontend"
}

resource "aws_s3_bucket_policy" "frontend" {
  bucket = aws_s3_bucket.frontend.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowCloudFrontRead"
        Effect    = "Allow"
        Principal = {
          AWS = aws_cloudfront_origin_access_identity.frontend.iam_arn
        }
        Action   = ["s3:GetObject"]
        Resource = ["${aws_s3_bucket.frontend.arn}/*"]
      }
    ]
  })
}

resource "aws_cloudfront_distribution" "frontend" {
  enabled             = true
  default_root_object = "index.html"

  origin {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id   = "s3-frontend-origin"
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.frontend.cloudfront_access_identity_path
    }
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "s3-frontend-origin"
    viewer_protocol_policy = "redirect-to-https"
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = var.certificate_arn == "" ? true : false
    acm_certificate_arn            = var.certificate_arn != "" ? var.certificate_arn : null
    ssl_support_method             = var.certificate_arn != "" ? "sni-only" : null
  }

  tags = {
    Name = "${var.environment}-frontend-cf"
  }
}

resource "aws_security_group" "alb" {
  name        = "${var.environment}-alb-sg"
  description = "Allow HTTP to ALB"
  vpc_id      = aws_vpc.main.id
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ecs" {
  name        = "${var.environment}-ecs-sg"
  description = "Allow traffic from ALB and outbound internet"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "db" {
  count       = var.create_rds ? 1 : 0
  name        = "${var.environment}-db-sg"
  description = "Allow ECS to reach RDS"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = var.db_engine == "postgres" ? 5432 : 3306
    to_port         = var.db_engine == "postgres" ? 5432 : 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb" "frontend" {
  name               = "${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [for s in aws_subnet.public : s.id]
  tags = {
    Name = "${var.environment}-alb"
  }
}

resource "aws_lb_target_group" "ecs" {
  name     = "${var.environment}-ecs-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
  health_check {
    path                = "/health"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.frontend.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ecs.arn
  }
}

resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.environment}-ecs-task-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Effect = "Allow"
      Sid    = ""
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_policy" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "ecs_secrets_manager_policy" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
}

resource "aws_iam_role" "ecs_task_role" {
  name = "${var.environment}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Effect = "Allow"
      Sid    = ""
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_dynamodb_policy" {
  count      = var.create_dynamodb ? 1 : 0
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/aws/ecs/${var.environment}-support-assistant"
  retention_in_days = 14
}

resource "aws_ecs_cluster" "main" {
  name = "${var.environment}-support-assistant-cluster"
}

resource "aws_ecs_task_definition" "backend" {
  family                   = "${var.environment}-support-assistant-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.container_cpu
  memory                   = var.container_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "support-assistant-backend"
      image     = "${aws_ecr_repository.backend.repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "AWS_REGION"
          value = var.aws_region
        },
        {
          name  = "OPENAI_MODEL"
          value = var.openai_model
        },
        {
          name  = "OPENAI_API_URL"
          value = var.openai_api_url
        }
      ]
      secrets = [
        {
          name      = "SN_INSTANCE_URL"
          valueFrom = aws_secretsmanager_secret.sn_instance_url.arn
        },
        {
          name      = "SN_USER"
          valueFrom = aws_secretsmanager_secret.sn_user.arn
        },
        {
          name      = "SN_PASS"
          valueFrom = aws_secretsmanager_secret.sn_pass.arn
        },
        {
          name      = "OPENAI_API_KEY"
          valueFrom = aws_secretsmanager_secret.openai_api_key.arn
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "support-assistant"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "backend" {
  name            = "${var.environment}-support-assistant-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = [for s in aws_subnet.private : s.id]
    security_groups = [aws_security_group.ecs.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.ecs.arn
    container_name   = "support-assistant-backend"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.http]
}

resource "aws_dynamodb_table" "sessions" {
  count       = var.create_dynamodb && !var.create_rds ? 1 : 0
  name        = "${var.environment}-support-assistant-sessions"
  billing_mode = "PAY_PER_REQUEST"
  hash_key    = "user_id"

  attribute {
    name = "user_id"
    type = "S"
  }

  tags = {
    Name = "${var.environment}-support-assistant-sessions"
  }
}

resource "random_password" "db" {
  count = var.create_rds ? 1 : 0
  length  = 16
  special = true
}

resource "aws_db_subnet_group" "main" {
  count = var.create_rds ? 1 : 0
  name  = "${var.environment}-db-subnet-group"

  subnet_ids = [for s in aws_subnet.private : s.id]
  tags = {
    Name = "${var.environment}-db-subnet-group"
  }
}

resource "aws_db_instance" "main" {
  count               = var.create_rds ? 1 : 0
  identifier          = "${var.environment}-support-assistant-db"
  engine              = var.db_engine
  instance_class      = var.db_instance_class
  allocated_storage   = var.db_allocated_storage
  name                = var.db_name
  username            = var.db_username
  password            = random_password.db[0].result
  db_subnet_group_name = aws_db_subnet_group.main[0].name
  vpc_security_group_ids = [aws_security_group.db[0].id]
  skip_final_snapshot = true
  publicly_accessible = false
  tags = {
    Name = "${var.environment}-support-assistant-db"
  }
}

resource "aws_secretsmanager_secret" "sn_instance_url" {
  name = "${var.environment}-sn-instance-url"
}
resource "aws_secretsmanager_secret_version" "sn_instance_url" {
  secret_id     = aws_secretsmanager_secret.sn_instance_url.id
  secret_string = var.sn_instance_url
}

resource "aws_secretsmanager_secret" "sn_user" {
  name = "${var.environment}-sn-user"
}
resource "aws_secretsmanager_secret_version" "sn_user" {
  secret_id     = aws_secretsmanager_secret.sn_user.id
  secret_string = var.sn_user
}

resource "aws_secretsmanager_secret" "sn_pass" {
  name = "${var.environment}-sn-pass"
}
resource "aws_secretsmanager_secret_version" "sn_pass" {
  secret_id     = aws_secretsmanager_secret.sn_pass.id
  secret_string = var.sn_pass
}

resource "aws_secretsmanager_secret" "openai_api_key" {
  name = "${var.environment}-openai-api-key"
}
resource "aws_secretsmanager_secret_version" "openai_api_key" {
  secret_id     = aws_secretsmanager_secret.openai_api_key.id
  secret_string = var.openai_api_key
}

resource "aws_secretsmanager_secret" "openai_model" {
  name = "${var.environment}-openai-model"
}
resource "aws_secretsmanager_secret_version" "openai_model" {
  secret_id     = aws_secretsmanager_secret.openai_model.id
  secret_string = var.openai_model
}

resource "aws_secretsmanager_secret" "openai_api_url" {
  name = "${var.environment}-openai-api-url"
}
resource "aws_secretsmanager_secret_version" "openai_api_url" {
  secret_id     = aws_secretsmanager_secret.openai_api_url.id
  secret_string = var.openai_api_url
}

resource "aws_s3_bucket_object" "frontend_index" {
  bucket = aws_s3_bucket.frontend.id
  key    = "index.html"
  source = "../frontend/index.html"
  content_type = "text/html"
}
