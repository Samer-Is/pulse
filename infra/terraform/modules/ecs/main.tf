# ECS Module - Cluster, Task Definitions, Services

locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${local.name_prefix}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "${local.name_prefix}-cluster"
  }
}

# ECS Task Definitions
resource "aws_ecs_task_definition" "frontend" {
  family                   = "${local.name_prefix}-frontend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  container_definitions = jsonencode([
    {
      name      = "frontend"
      image     = "${var.ecr_repository_urls["frontend"]}:latest"
      essential = true
      
      portMappings = [
        {
          containerPort = 3000
          protocol      = "tcp"
        }
      ]

      environment = [
        { name = "NODE_ENV", value = var.environment == "prod" ? "production" : "development" },
        { name = "NEXT_PUBLIC_API_BASE", value = var.api_base_url },
        { name = "NEXT_PUBLIC_GATEWAY_BASE", value = var.gateway_base_url }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = var.log_group_frontend
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    Name = "${local.name_prefix}-frontend-task"
  }
}

resource "aws_ecs_task_definition" "backend" {
  family                   = "${local.name_prefix}-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = "${var.ecr_repository_urls["backend"]}:latest"
      essential = true
      
      portMappings = [
        {
          containerPort = 8080
          protocol      = "tcp"
        }
      ]

      environment = [
        { name = "ENV", value = var.environment },
        { name = "AWS_REGION", value = var.aws_region }
      ]

      secrets = [
        { name = "DATABASE_URL", valueFrom = "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:AI_STUDIO_DATABASE_URL" },
        { name = "REDIS_URL", valueFrom = "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:AI_STUDIO_REDIS_URL" },
        { name = "JWT_SECRET", valueFrom = "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:AI_STUDIO_JWT_SECRET" }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = var.log_group_backend
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    Name = "${local.name_prefix}-backend-task"
  }
}

resource "aws_ecs_task_definition" "gateway" {
  family                   = "${local.name_prefix}-gateway"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  container_definitions = jsonencode([
    {
      name      = "gateway"
      image     = "${var.ecr_repository_urls["gateway"]}:latest"
      essential = true
      
      portMappings = [
        {
          containerPort = 8081
          protocol      = "tcp"
        }
      ]

      environment = [
        { name = "ENV", value = var.environment },
        { name = "AWS_REGION", value = var.aws_region }
      ]

      secrets = [
        { name = "OPENAI_API_KEY", valueFrom = "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:OPENAI_API_KEY" },
        { name = "ANTHROPIC_API_KEY", valueFrom = "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:ANTHROPIC_API_KEY" },
        { name = "REDIS_URL", valueFrom = "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:AI_STUDIO_REDIS_URL" }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = var.log_group_gateway
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    Name = "${local.name_prefix}-gateway-task"
  }
}

resource "aws_ecs_task_definition" "worker" {
  family                   = "${local.name_prefix}-worker"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  container_definitions = jsonencode([
    {
      name      = "worker"
      image     = "${var.ecr_repository_urls["worker"]}:latest"
      essential = true

      environment = [
        { name = "ENV", value = var.environment },
        { name = "AWS_REGION", value = var.aws_region }
      ]

      secrets = [
        { name = "DATABASE_URL", valueFrom = "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:AI_STUDIO_DATABASE_URL" },
        { name = "REDIS_URL", valueFrom = "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:AI_STUDIO_REDIS_URL" }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = var.log_group_worker
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    Name = "${local.name_prefix}-worker-task"
  }
}

# ECS Services
resource "aws_ecs_service" "frontend" {
  name            = "${local.name_prefix}-frontend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.frontend.arn
  desired_count   = var.frontend_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = var.frontend_target_group_arn
    container_name   = "frontend"
    container_port   = 3000
  }

  depends_on = [var.alb_listener_arn]

  tags = {
    Name = "${local.name_prefix}-frontend-service"
  }
}

resource "aws_ecs_service" "backend" {
  name            = "${local.name_prefix}-backend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = var.backend_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = var.backend_target_group_arn
    container_name   = "backend"
    container_port   = 8080
  }

  depends_on = [var.alb_listener_arn]

  tags = {
    Name = "${local.name_prefix}-backend-service"
  }
}

resource "aws_ecs_service" "gateway" {
  name            = "${local.name_prefix}-gateway"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.gateway.arn
  desired_count   = var.gateway_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = var.gateway_target_group_arn
    container_name   = "gateway"
    container_port   = 8081
  }

  depends_on = [var.alb_listener_arn]

  tags = {
    Name = "${local.name_prefix}-gateway-service"
  }
}

resource "aws_ecs_service" "worker" {
  name            = "${local.name_prefix}-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count   = var.worker_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = false
  }

  tags = {
    Name = "${local.name_prefix}-worker-service"
  }
}

