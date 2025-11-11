#!/bin/bash
set -e

ENVIRONMENT=${1:-dev}
PROJECT_ID="upbeat-arch-477806-k8"

echo "🚀 Deploying to $ENVIRONMENT..."

# Check API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "❌ Error: ANTHROPIC_API_KEY not set"
  exit 1
fi

# Build function package
echo "📦 Building Cloud Function..."
cd ../backend
rm -rf package function.zip
mkdir -p package
pip3 install -r requirements.txt -t package/ --quiet
cd package && zip -r ../function.zip . > /dev/null
cd .. && zip -g function.zip *.py > /dev/null
cd ../terraform

# Initialize Terraform
echo "🔧 Initializing Terraform..."
terraform init -input=false

# Select workspace
if terraform workspace list 2>/dev/null | grep -q "$ENVIRONMENT"; then
  terraform workspace select $ENVIRONMENT
else
  terraform workspace new $ENVIRONMENT
fi

# Apply
echo "🚀 Deploying infrastructure..."
terraform apply \
  -var="environment=$ENVIRONMENT" \
  -var="anthropic_api_key=$ANTHROPIC_API_KEY" \
  -auto-approve

# Show outputs
echo ""
echo "✅ Deployment complete!"
echo ""
terraform output
