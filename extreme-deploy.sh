#!/bin/bash

echo "⚡ EXTREME MINIMAL Flask API Deployment"
echo "======================================"
echo ""
echo "🎯 AGGRESSIVE OPTIMIZATIONS:"
echo "  • Ultra-lightweight model (paraphrase-MiniLM-L3-v2) - 22MB"
echo "  • DISABLED: ONNX, OpenVINO model downloads"
echo "  • ONLY PyTorch format loaded"
echo "  • Extended worker timeout: 600s (10 minutes)"
echo "  • Minimal dependencies with --no-deps flags"
echo "  • Temporary model cache in /tmp"
echo ""
echo "📊 Expected Results:"
echo "  • Image size: ~600MB (vs 5.7GB original)"
echo "  • Memory usage: 200-300MB"
echo "  • Model files: ~70MB (vs 400MB+ all formats)"
echo "  • Startup time: 5-10 seconds"
echo "  • NO WORKER TIMEOUTS"
echo ""

echo "🔨 Building EXTREME minimal image..."
echo "Command: docker build -f Dockerfile.extreme-minimal -t st-flask:extreme ."
echo ""

echo "🚀 Deploy with EXTENDED TIMEOUT (600s):"
echo ""
echo "# Stop current container"
echo "docker stop st-flask-container 2>/dev/null || true"
echo "docker rm st-flask-container 2>/dev/null || true"
echo ""
echo "# Deploy extreme minimal container"
echo "docker run -d \\"
echo "  --name st-flask-container \\"
echo "  --restart unless-stopped \\"
echo "  -p 5001:5001 \\"
echo "  --memory=400m \\"
echo "  --memory-swap=400m \\"
echo "  -e MODEL_NAME='paraphrase-MiniLM-L3-v2' \\"
echo "  -e SENTENCE_TRANSFORMERS_DISABLE_ONNX=1 \\"
echo "  -e SENTENCE_TRANSFORMERS_DISABLE_OPENVINO=1 \\"
echo "  -e MONGODB_URI='mongodb+srv://nishanshashinthalive:NQGLM8NUZcZP5QlY@n8n-automation-data.2ednq1p.mongodb.net/?retryWrites=true&w=majority&appName=n8n-automation-data' \\"
echo "  -e MONGODB_DATABASE='automation_with_ai_data' \\"
echo "  -e MONGODB_COLLECTION='knowledge_base' \\"
echo "  -e SIMILARITY_THRESHOLD='0.6' \\"
echo "  st-flask:extreme"
echo ""

echo "📋 Monitor deployment:"
echo "  docker logs -f st-flask-container  # Should show MUCH faster startup"
echo "  docker stats st-flask-container    # Should use ~200-300MB RAM"
echo "  curl http://localhost:5001/health  # Should respond in 1-2 seconds"
echo ""

echo "🎉 This EXTREME optimization should COMPLETELY eliminate:"
echo "  ❌ Worker timeouts (600s vs 120s timeout)"
echo "  ❌ Multiple model format downloads (ONNX, OpenVINO disabled)"
echo "  ❌ High memory usage (400MB limit vs 2GB+)"
echo "  ❌ Slow startup (minimal model loading)"
echo ""

echo "🔥 If this still times out, the issue is NOT the model size!"
echo "    Check server network connectivity or increase timeout further."

# Ask if user wants to build
read -p "Build extreme minimal image now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔨 Building extreme minimal image..."
    docker build -f Dockerfile.extreme-minimal -t st-flask:extreme .
    
    if [ $? -eq 0 ]; then
        echo "✅ Build successful!"
        echo "📏 Image size:"
        docker images st-flask:extreme
        echo ""
        echo "🚀 Ready to deploy with the commands above!"
    else
        echo "❌ Build failed. Check the logs above."
    fi
fi 