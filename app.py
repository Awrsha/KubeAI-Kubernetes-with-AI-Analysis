import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from kubernetes import client, config
import datetime

app = Flask(__name__)

# API Keys
GROQ_API_KEY = os.environ.get('GROQ_API_KEY') or ""
HUGGINGFACE_TOKEN = os.environ.get('HUGGINGFACE_TOKEN') or ""

# Try to load Kubernetes config from default locations
try:
    config.load_kube_config()
    k8s_available = True
except:
    try:
        config.load_incluster_config()
        k8s_available = True
    except:
        k8s_available = False
        print("Warning: Kubernetes configuration not found. Running in demo mode.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/cluster-overview')
def cluster_overview():
    if not k8s_available:
        # Return mock data for demo mode
        return jsonify({
            'nodes': 5,
            'pods': 45,
            'deployments': 12,
            'services': 18,
            'cpu_usage': 43,
            'memory_usage': 38,
            'storage_usage': 22,
            'health_status': 'Healthy',
            'uptime': '14d 6h 32m'
        })
    
    try:
        # Real implementation would query the Kubernetes API
        v1 = client.CoreV1Api()
        apps_v1 = client.AppsV1Api()
        
        nodes = v1.list_node().items
        pods = v1.list_pod_for_all_namespaces().items
        deployments = apps_v1.list_deployment_for_all_namespaces().items
        services = v1.list_service_for_all_namespaces().items
        
        # This is simplified - real implementation would calculate actual usage
        return jsonify({
            'nodes': len(nodes),
            'pods': len(pods),
            'deployments': len(deployments),
            'services': len(services),
            'cpu_usage': 43,  # Mock values for demo
            'memory_usage': 38,
            'storage_usage': 22,
            'health_status': 'Healthy',
            'uptime': '14d 6h 32m'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/resources')
def get_resources():
    if not k8s_available:
        # Return mock data for demo mode
        return jsonify({
            'pods': generate_mock_pods(),
            'deployments': generate_mock_deployments(),
            'services': generate_mock_services()
        })
    
    try:
        v1 = client.CoreV1Api()
        apps_v1 = client.AppsV1Api()
        
        pods = []
        for pod in v1.list_pod_for_all_namespaces().items:
            containers = pod.spec.containers
            status = pod.status.phase
            ready_containers = sum(1 for cs in pod.status.container_statuses if cs.ready) if pod.status.container_statuses else 0
            total_containers = len(containers)
            
            pods.append({
                'name': pod.metadata.name,
                'namespace': pod.metadata.namespace,
                'status': status,
                'ready': f"{ready_containers}/{total_containers}",
                'age': get_age(pod.metadata.creation_timestamp),
                'ip': pod.status.pod_ip
            })
        
        deployments = []
        for dep in apps_v1.list_deployment_for_all_namespaces().items:
            deployments.append({
                'name': dep.metadata.name,
                'namespace': dep.metadata.namespace,
                'replicas': f"{dep.status.ready_replicas or 0}/{dep.spec.replicas}",
                'age': get_age(dep.metadata.creation_timestamp)
            })
        
        services = []
        for svc in v1.list_service_for_all_namespaces().items:
            port_info = []
            for port in svc.spec.ports:
                port_info.append(f"{port.port}:{port.target_port}/{port.protocol}")
            
            services.append({
                'name': svc.metadata.name,
                'namespace': svc.metadata.namespace,
                'type': svc.spec.type,
                'cluster_ip': svc.spec.cluster_ip,
                'ports': ", ".join(port_info),
                'age': get_age(svc.metadata.creation_timestamp)
            })
        
        return jsonify({
            'pods': pods,
            'deployments': deployments,
            'services': services
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/anomalies')
def get_anomalies():
    # In a real implementation, this would analyze logs and metrics
    # Here we'll use GROQ API to simulate AI analysis
    
    prompt = """
    Analyze the following Kubernetes metrics and identify potential anomalies or issues:
    - Pod restarts in last 24h: [12, 0, 0, 5, 0, 1, 0, 0, 0, 3]
    - CPU usage spikes: [35%, 42%, 38%, 82%, 45%, 39%, 41%, 40%]
    - Memory usage: [62%, 65%, 63%, 92%, 68%, 64%, 67%, 65%]
    - API server latency: [120ms, 105ms, 230ms, 110ms, 108ms]
    
    Return exactly 3 anomalies in JSON format with the following structure:
    [
        {
            "component": "component name",
            "issue": "brief description of the issue",
            "severity": "High/Medium/Low",
            "recommendation": "brief recommendation"
        }
    ]
    Return only the JSON array with no additional text or formatting.
    """
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            try:
                # Try to parse the content as JSON
                anomalies = json.loads(content)
                return jsonify(anomalies)
            except json.JSONDecodeError:
                # If parsing fails, return the raw content
                return jsonify([
                    {
                        "component": "api-server",
                        "issue": "High latency spike detected",
                        "severity": "Medium",
                        "recommendation": "Check for resource constraints or network issues"
                    },
                    {
                        "component": "pod-frontend-7d8f9b5c4d",
                        "issue": "Multiple pod restarts",
                        "severity": "High",
                        "recommendation": "Check pod logs and events for error messages"
                    },
                    {
                        "component": "database-service",
                        "issue": "Memory usage near capacity",
                        "severity": "High",
                        "recommendation": "Increase memory limits or optimize application"
                    }
                ])
        else:
            # Fallback to mock data if API call fails
            return jsonify([
                {
                    "component": "api-server",
                    "issue": "High latency spike detected",
                    "severity": "Medium",
                    "recommendation": "Check for resource constraints or network issues"
                },
                {
                    "component": "pod-frontend-7d8f9b5c4d",
                    "issue": "Multiple pod restarts",
                    "severity": "High",
                    "recommendation": "Check pod logs and events for error messages"
                },
                {
                    "component": "database-service",
                    "issue": "Memory usage near capacity",
                    "severity": "High",
                    "recommendation": "Increase memory limits or optimize application"
                }
            ])
    except Exception as e:
        # Return mock data on error
        return jsonify([
            {
                "component": "api-server",
                "issue": "High latency spike detected",
                "severity": "Medium",
                "recommendation": "Check for resource constraints or network issues"
            },
            {
                "component": "pod-frontend-7d8f9b5c4d",
                "issue": "Multiple pod restarts",
                "severity": "High",
                "recommendation": "Check pod logs and events for error messages"
            },
            {
                "component": "database-service",
                "issue": "Memory usage near capacity",
                "severity": "High",
                "recommendation": "Increase memory limits or optimize application"
            }
        ])

@app.route('/api/optimization')
def get_optimization():
    # In a real implementation, this would analyze the cluster configuration
    # Here we'll use GROQ API to generate optimization recommendations
    
    prompt = """
    Generate 3 specific optimization recommendations for a Kubernetes cluster with these characteristics:
    - 5 nodes (each 4 CPUs, 16GB RAM)
    - 45 pods across 12 deployments
    - Average CPU utilization: 43%
    - Average memory utilization: 38%
    - Multiple services with no resource limits defined
    - No horizontal pod autoscaling configured
    
    Return the recommendations in JSON format with this structure:
    [
        {
            "title": "brief title",
            "description": "detailed explanation",
            "impact": "High/Medium/Low",
            "implementation": "how to implement"
        }
    ]
    Return only the JSON array with no additional text or formatting.
    """
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            try:
                # Try to parse the content as JSON
                recommendations = json.loads(content)
                return jsonify(recommendations)
            except json.JSONDecodeError:
                # If parsing fails, return the raw content
                return jsonify([
                    {
                        "title": "Implement Resource Limits",
                        "description": "Services without defined resource limits can consume excessive resources, impacting cluster stability and causing resource contention.",
                        "impact": "High",
                        "implementation": "Add CPU and memory limits to all deployments with 'resources.limits' field in YAML configuration."
                    },
                    {
                        "title": "Configure Horizontal Pod Autoscaling",
                        "description": "Implementing HPA will automatically scale resources based on CPU/memory utilization, improving efficiency and availability.",
                        "impact": "Medium",
                        "implementation": "Create HorizontalPodAutoscaler resources targeting deployments with high variability in load."
                    },
                    {
                        "title": "Implement Pod Disruption Budgets",
                        "description": "PDAs ensure availability during voluntary disruptions like upgrades, preventing service outages.",
                        "impact": "Medium",
                        "implementation": "Define PodDisruptionBudget resources for critical services, specifying minAvailable."
                    }
                ])
        else:
            # Fallback to mock data if API call fails
            return jsonify([
                {
                    "title": "Implement Resource Limits",
                    "description": "Services without defined resource limits can consume excessive resources, impacting cluster stability and causing resource contention.",
                    "impact": "High",
                    "implementation": "Add CPU and memory limits to all deployments with 'resources.limits' field in YAML configuration."
                },
                {
                    "title": "Configure Horizontal Pod Autoscaling",
                    "description": "Implementing HPA will automatically scale resources based on CPU/memory utilization, improving efficiency and availability.",
                    "impact": "Medium",
                    "implementation": "Create HorizontalPodAutoscaler resources targeting deployments with high variability in load."
                },
                {
                    "title": "Implement Pod Disruption Budgets",
                    "description": "PDAs ensure availability during voluntary disruptions like upgrades, preventing service outages.",
                    "impact": "Medium",
                    "implementation": "Define PodDisruptionBudget resources for critical services, specifying minAvailable."
                }
            ])
    except Exception as e:
        # Return mock data on error
        return jsonify([
            {
                "title": "Implement Resource Limits",
                "description": "Services without defined resource limits can consume excessive resources, impacting cluster stability and causing resource contention.",
                "impact": "High",
                "implementation": "Add CPU and memory limits to all deployments with 'resources.limits' field in YAML configuration."
            },
            {
                "title": "Configure Horizontal Pod Autoscaling",
                "description": "Implementing HPA will automatically scale resources based on CPU/memory utilization, improving efficiency and availability.",
                "impact": "Medium",
                "implementation": "Create HorizontalPodAutoscaler resources targeting deployments with high variability in load."
            },
            {
                "title": "Implement Pod Disruption Budgets",
                "description": "PDAs ensure availability during voluntary disruptions like upgrades, preventing service outages.",
                "impact": "Medium",
                "implementation": "Define PodDisruptionBudget resources for critical services, specifying minAvailable."
            }
        ])

@app.route('/api/generate-command', methods=['POST'])
def generate_command():
    data = request.json
    natural_language = data.get('prompt', '')
    
    if not natural_language:
        return jsonify({"error": "No prompt provided"}), 400
    
    # Use GROQ to generate kubectl commands from natural language
    prompt = f"""
    Convert the following natural language request into a valid kubectl command:
    "{natural_language}"
    
    Return only the kubectl command with no additional explanations or notes.
    """
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            command = result['choices'][0]['message']['content'].strip()
            return jsonify({"command": command})
        else:
            # Generate a reasonable response based on common patterns
            if "get pods" in natural_language.lower():
                return jsonify({"command": "kubectl get pods -A"})
            elif "deployment" in natural_language.lower() and "scale" in natural_language.lower():
                return jsonify({"command": "kubectl scale deployment/nginx-deployment --replicas=3"})
            elif "log" in natural_language.lower():
                return jsonify({"command": "kubectl logs pod/nginx-pod-1a2b3c"})
            else:
                return jsonify({"command": "kubectl get all -n default"})
    except Exception as e:
        # Provide fallback command generation
        if "get pods" in natural_language.lower():
            return jsonify({"command": "kubectl get pods -A"})
        elif "deployment" in natural_language.lower() and "scale" in natural_language.lower():
            return jsonify({"command": "kubectl scale deployment/nginx-deployment --replicas=3"})
        elif "log" in natural_language.lower():
            return jsonify({"command": "kubectl logs pod/nginx-pod-1a2b3c"})
        else:
            return jsonify({"command": "kubectl get all -n default"})

@app.route('/api/activities')
def get_activities():
    # In a real implementation, this would fetch actual cluster events
    # Here we'll return mock data
    
    activities = [
        {
            "timestamp": "2023-07-15T14:32:21Z",
            "component": "Deployment/frontend",
            "action": "Scaled",
            "description": "Scaled replicas from 3 to 5",
            "user": "admin"
        },
        {
            "timestamp": "2023-07-15T13:18:05Z",
            "component": "Pod/redis-cache-5d8c7b9f68-abcde",
            "action": "Created",
            "description": "Created container redis",
            "user": "system"
        },
        {
            "timestamp": "2023-07-15T13:17:52Z",
            "component": "Deployment/redis-cache",
            "action": "Created",
            "description": "Created deployment with 3 replicas",
            "user": "admin"
        },
        {
            "timestamp": "2023-07-15T12:45:10Z",
            "component": "Pod/nginx-ingress-controller-7d8f9b5c4d-2abcd",
            "action": "Restarted",
            "description": "Container restarted due to liveness probe failure",
            "user": "system"
        },
        {
            "timestamp": "2023-07-15T11:32:18Z",
            "component": "Service/backend-api",
            "action": "Updated",
            "description": "Updated service port from 8080 to 9000",
            "user": "admin"
        },
        {
            "timestamp": "2023-07-15T10:15:43Z",
            "component": "ConfigMap/app-config",
            "action": "Updated",
            "description": "Updated configuration values",
            "user": "jenkins-ci"
        }
    ]
    
    return jsonify(activities)

# Helper functions for mocking data
def get_age(timestamp):
    if not timestamp:
        return "Unknown"
    now = datetime.datetime.now(timestamp.tzinfo)
    diff = now - timestamp
    days = diff.days
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    if days > 0:
        return f"{days}d"
    elif hours > 0:
        return f"{hours}h"
    else:
        return f"{minutes}m"

def generate_mock_pods():
    return [
        {
            'name': 'nginx-deployment-66b6c48dd5-7b9tx',
            'namespace': 'default',
            'status': 'Running',
            'ready': '1/1',
            'age': '3d',
            'ip': '10.244.0.15'
        },
        {
            'name': 'redis-master-5d8c7b9f68-q2btp',
            'namespace': 'data',
            'status': 'Running',
            'ready': '1/1',
            'age': '5d',
            'ip': '10.244.0.16'
        },
        {
            'name': 'mongodb-0',
            'namespace': 'data',
            'status': 'Running',
            'ready': '1/1',
            'age': '2d',
            'ip': '10.244.0.17'
        },
        {
            'name': 'frontend-deployment-7d8f9b5c4d-xzlp9',
            'namespace': 'web',
            'status': 'Running',
            'ready': '1/1',
            'age': '1d',
            'ip': '10.244.0.18'
        },
        {
            'name': 'api-deployment-5b554f484b-abc12',
            'namespace': 'web',
            'status': 'Running',
            'ready': '1/1',
            'age': '6h',
            'ip': '10.244.0.19'
        }
    ]

def generate_mock_deployments():
    return [
        {
            'name': 'nginx-deployment',
            'namespace': 'default',
            'replicas': '3/3',
            'age': '3d'
        },
        {
            'name': 'redis-master',
            'namespace': 'data',
            'replicas': '1/1',
            'age': '5d'
        },
        {
            'name': 'frontend-deployment',
            'namespace': 'web',
            'replicas': '5/5',
            'age': '1d'
        },
        {
            'name': 'api-deployment',
            'namespace': 'web',
            'replicas': '2/2',
            'age': '6h'
        }
    ]

def generate_mock_services():
    return [
        {
            'name': 'kubernetes',
            'namespace': 'default',
            'type': 'ClusterIP',
            'cluster_ip': '10.96.0.1',
            'ports': '443:443/TCP',
            'age': '30d'
        },
        {
            'name': 'nginx-service',
            'namespace': 'default',
            'type': 'ClusterIP',
            'cluster_ip': '10.96.0.15',
            'ports': '80:8080/TCP',
            'age': '3d'
        },
        {
            'name': 'redis-service',
            'namespace': 'data',
            'type': 'ClusterIP',
            'cluster_ip': '10.96.0.16',
            'ports': '6379:6379/TCP',
            'age': '5d'
        },
        {
            'name': 'mongodb-service',
            'namespace': 'data',
            'type': 'ClusterIP',
            'cluster_ip': '10.96.0.17',
            'ports': '27017:27017/TCP',
            'age': '2d'
        },
        {
            'name': 'frontend-service',
            'namespace': 'web',
            'type': 'LoadBalancer',
            'cluster_ip': '10.96.0.18',
            'ports': '80:80/TCP',
            'age': '1d'
        },
        {
            'name': 'api-service',
            'namespace': 'web',
            'type': 'ClusterIP',
            'cluster_ip': '10.96.0.19',
            'ports': '8080:8080/TCP',
            'age': '6h'
        }
    ]

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))