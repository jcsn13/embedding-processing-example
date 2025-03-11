# Makefile for Terraform deployment

# Include environment variables from .env file
include .env
export

# Default target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  init     - Initialize Terraform"
	@echo "  plan     - Create a Terraform plan"
	@echo "  apply    - Apply Terraform changes"
	@echo "  destroy  - Destroy all resources"
	@echo "  clean    - Clean up local Terraform files"
	@echo "  validate - Validate Terraform configuration"
	@echo "  deploy   - Deploy the entire infrastructure (init + apply)"

# Initialize Terraform
.PHONY: init
init:
	@echo "Initializing Terraform..."
	cd terraform && terraform init

# Create a Terraform vars file
terraform/terraform.tfvars:
	@echo "Creating Terraform variables file..."
	@echo 'project_id = "$(PROJECT_ID)"' > terraform/terraform.tfvars
	@echo 'project_number = "$(PROJECT_NUMBER)"' >> terraform/terraform.tfvars
	@echo 'region = "$(REGION)"' >> terraform/terraform.tfvars
	@echo 'bucket_name = "$(BUCKET_NAME)"' >> terraform/terraform.tfvars
	@echo 'cloud_function_name = "$(CLOUD_FUNCTION_NAME)"' >> terraform/terraform.tfvars
	@echo 'streamlit_app_name = "$(STREAMLIT_APP_NAME)"' >> terraform/terraform.tfvars
	@echo 'function_memory = "$(FUNCTION_MEMORY)"' >> terraform/terraform.tfvars
	@echo 'function_timeout = "$(FUNCTION_TIMEOUT)"' >> terraform/terraform.tfvars
	@echo 'streamlit_memory = "$(STREAMLIT_MEMORY)"' >> terraform/terraform.tfvars
	@echo 'embedding_dimensions = $(EMBEDDING_DIMENSIONS)' >> terraform/terraform.tfvars
	@echo 'embedding_model = "$(EMBEDDING_MODEL)"' >> terraform/terraform.tfvars
	@echo 'embedding_model_name = "$(EMBEDDING_MODEL_NAME)"' >> terraform/terraform.tfvars
	@echo 'sectors = [' >> terraform/terraform.tfvars
	@SECTOR_LIST=$$(echo $(SECTORS) | tr ' ' '\n' | sed 's/"//g'); \
	for sector in $$SECTOR_LIST; do \
		if [ -z "$$sector" ]; then \
			continue; \
		fi; \
		if [ "$$sector" = "$$(echo "$$SECTOR_LIST" | tail -n1)" ]; then \
			echo '  "'$$sector'"' >> terraform/terraform.tfvars; \
		else \
			echo '  "'$$sector'",' >> terraform/terraform.tfvars; \
		fi; \
	done
	@echo ']' >> terraform/terraform.tfvars
	@echo 'fixed_size_chunk_size = $(FIXED_SIZE_CHUNK_SIZE)' >> terraform/terraform.tfvars
	@echo 'semantic_min_chunk_size = $(SEMANTIC_MIN_CHUNK_SIZE)' >> terraform/terraform.tfvars
	@echo 'semantic_max_chunk_size = $(SEMANTIC_MAX_CHUNK_SIZE)' >> terraform/terraform.tfvars
	@echo 'sliding_window_chunk_size = $(SLIDING_WINDOW_CHUNK_SIZE)' >> terraform/terraform.tfvars
	@echo 'sliding_window_overlap = $(SLIDING_WINDOW_OVERLAP)' >> terraform/terraform.tfvars
	# hierarchical_levels is hardcoded in cloud_function/config.py
	@echo 'sectors_collection = "$(SECTORS_COLLECTION)"' >> terraform/terraform.tfvars
	@echo 'documents_collection = "$(DOCUMENTS_COLLECTION)"' >> terraform/terraform.tfvars
	@echo 'chunks_collection = "$(CHUNKS_COLLECTION)"' >> terraform/terraform.tfvars
	@echo 'temp_directory = "$(TEMP_DIRECTORY)"' >> terraform/terraform.tfvars

# Create a Terraform plan
.PHONY: plan
plan: terraform/terraform.tfvars
	@echo "Creating Terraform plan..."
	cd terraform && terraform plan

# Apply Terraform changes
.PHONY: apply
apply: terraform/terraform.tfvars
	@echo "Applying Terraform changes..."
	cd terraform && terraform apply -auto-approve

# Destroy all resources
.PHONY: destroy
destroy: terraform/terraform.tfvars
	@echo "Destroying all resources..."
	cd terraform && terraform destroy -auto-approve

# Clean up local Terraform files
.PHONY: clean
clean:
	@echo "Cleaning up local Terraform files..."
	rm -rf terraform/.terraform terraform/.terraform.lock.hcl terraform/terraform.tfstate terraform/terraform.tfstate.backup terraform/terraform.tfvars

# Validate Terraform configuration
.PHONY: validate
validate:
	@echo "Validating Terraform configuration..."
	cd terraform && terraform validate

# Deploy the entire infrastructure
.PHONY: deploy
deploy: init apply
	@echo "Deployment complete!"
	@echo "Cloud Function URL: $$(cd terraform && terraform output -raw cloud_function_url)"
	@echo "Streamlit App URL: $$(cd terraform && terraform output -raw streamlit_app_url)"
