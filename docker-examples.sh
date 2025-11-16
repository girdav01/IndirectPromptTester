#!/bin/bash
# Docker usage examples for Indirect Prompt Tester

echo "=== Indirect Prompt Tester - Docker Examples ==="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Example 1: Start the application with Docker Compose${NC}"
echo "docker-compose up -d"
echo ""

echo -e "${BLUE}Example 2: Generate a file using CLI in container${NC}"
echo "docker-compose exec indirect-prompt-tester python -m indirect_prompt_tester.cli.main generate \\"
echo "    --type image \\"
echo "    --prompt 'Test indirect prompt' \\"
echo "    --output test.png \\"
echo "    --method visible"
echo ""

echo -e "${BLUE}Example 3: List available prompts${NC}"
echo "docker-compose exec indirect-prompt-tester python -m indirect_prompt_tester.cli.main list_prompts"
echo ""

echo -e "${BLUE}Example 4: Distribute a file via web hosting${NC}"
echo "docker-compose exec indirect-prompt-tester python -m indirect_prompt_tester.cli.main distribute \\"
echo "    --file generated_files/test.png \\"
echo "    --method web"
echo ""

echo -e "${BLUE}Example 5: View container logs${NC}"
echo "docker-compose logs -f indirect-prompt-tester"
echo ""

echo -e "${BLUE}Example 6: Stop the container${NC}"
echo "docker-compose down"
echo ""

echo -e "${BLUE}Example 7: Rebuild the image${NC}"
echo "docker-compose build --no-cache"
echo ""

echo -e "${BLUE}Example 8: Run CLI command directly${NC}"
echo "docker run -it --rm \\"
echo "  -v \$(pwd)/generated_files:/app/generated_files \\"
echo "  -v \$(pwd)/.env:/app/.env:ro \\"
echo "  indirect-prompt-tester \\"
echo "  python -m indirect_prompt_tester.cli.main generate \\"
echo "    --type document --format docx --prompt 'Your prompt' --output test.docx"
echo ""

echo -e "${GREEN}For more examples, see DOCKER.md${NC}"

