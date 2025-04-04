# KubeAI 🚀
  
  [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
  [![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
  [![Kubernetes](https://img.shields.io/badge/Kubernetes-1.22+-326CE5.svg?style=for-the-badge&logo=kubernetes&logoColor=white)](https://kubernetes.io/)
  [![AI-Powered](https://img.shields.io/badge/AI-Powered-FF5A5F.svg?style=for-the-badge&logo=artificial-intelligence&logoColor=white)](https://groq.com/)

  <p>A modern Kubernetes management dashboard with AI-powered analysis and insights</p>
</div>

<p align="center">
  <img src="https://github.com/Awrsha/KubeAI-Kubernetes-with-AI-Analysis/blob/master/dashboard.png" alt="KubeAI Dashboard" width="800" style="max-width: 100%; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
</p>

## 🌟 Features

| Feature | Description |
|---------|-------------|
| 🔍 **Cluster Visualization** | Interactive dashboard showing pods, deployments, services, and nodes |
| 🤖 **AI Command Generator** | Natural language to kubectl command conversion |
| 🧠 **Anomaly Detection** | AI-powered detection of unusual cluster behavior |
| ⚡ **Optimization Recommendations** | Get AI-suggested performance improvements |
| 📊 **Resource Metrics** | Live CPU, memory, and storage usage monitoring |
| 📝 **Activity Logging** | Chronological record of cluster events |


## 📚 Technology Stack

- **Frontend**: HTML5, TailwindCSS, JavaScript
- **Backend**: Python, Flask
- **AI Integration**: GROQ API, Hugging Face Transformers
- **Kubernetes**: Official Python K8s Client
- **UI Design**: Inspired by Zoox and Apple design systems

## 🔧 Installation

### Prerequisites

- Python 3.8+
- Kubernetes cluster with configured `kubeconfig`
- API keys for GROQ and Hugging Face

### Setting up environment variables

```bash
export GROQ_API_KEY="your_groq_api_key"
export HUGGINGFACE_TOKEN="your_huggingface_token"
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/Awrsha/KubeAI-Kubernetes-with-AI-Analysis.git
cd kubeai

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Using Docker

```bash
# Build the image
docker build -t kubeai:latest .

# Run the container
docker run -p 5000:5000 \
  -e GROQ_API_KEY="your_groq_api_key" \
  -e HUGGINGFACE_TOKEN="your_huggingface_token" \
  -v ~/.kube/config:/root/.kube/config \
  kubeai:latest
```

## 🚀 Usage

After starting the application, navigate to `http://localhost:5000` in your web browser.

### AI Command Generator

Convert natural language to kubectl commands:

### Anomaly Detection

KubeAI automatically identifies potential issues in your cluster:

-   **High CPU Usage**: Identifies pods consuming excessive CPU resources
-   **Frequent Restarts**: Detects pods with abnormal restart patterns
-   **Memory Leaks**: Identifies potential memory leaks in applications
-   **Network Issues**: Detects unusual network traffic patterns or latency

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the repository
2.  Create your feature branch (`git checkout -b feature/amazing-feature`)
3.  Commit your changes (`git commit -m 'Add some amazing feature'`)
4.  Push to the branch (`git push origin feature/amazing-feature`)
5.  Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](https://poe.com/chat/LICENSE) file for details.

## 🙏 Acknowledgements

-   [Kubernetes Python Client](https://github.com/kubernetes-client/python)
-   [GROQ API](https://groq.com/) for AI text generation
-   [Hugging Face](https://huggingface.co/) for AI model hosting
-   [TailwindCSS](https://tailwindcss.com/) for the UI components
-   [Flask](https://flask.palletsprojects.com/) for the web framework
