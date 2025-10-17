# 300 - Learning Our Subject

# Learning Kubernetes

A hands-on learning repository demonstrating Kubernetes concepts through a security-focused microservices application.

## Project Overview

This repository contains a complete **Secure Notes Application** deployed on Kubernetes, demonstrating core concepts and security best practices relevant to cybersecurity engineering.

### Application Architecture

- **Frontend**: Nginx serving a simple web interface
- **Backend API**: Python Flask REST API for managing secure notes
- **Database**: PostgreSQL with persistent storage
- **Security Features**: Network policies, RBAC, secrets management, security contexts

## What This Demonstrates

### Core Kubernetes Concepts

- **Pods**: Basic deployment units
- **Deployments**: Declarative application updates and scaling
- **Services**: Internal and external service discovery
- **ConfigMaps**: Non-sensitive configuration management
- **Secrets**: Sensitive data handling (database credentials, API keys)
- **PersistentVolumes**: Stateful application data storage
- **Namespaces**: Resource isolation

### Security Best Practices

- **NetworkPolicies**: Microsegmentation and traffic control
- **SecurityContext**: Running containers as non-root users
- **RBAC**: Role-based access control
- **Resource Limits**: Prevention of resource exhaustion attacks
- **Secret Management**: Proper handling of sensitive data
- **Health Checks**: Liveness and readiness probes

## Repository Structure

```
Learning-Kubernetes/
├── 300/README.md
├── app/
│   ├── backend/
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── frontend/
│       ├── index.html
│       ├── style.css
│       └── Dockerfile
└── k8s/
    ├── namespace.yaml
    ├── configmap.yaml
    ├── secrets.yaml
    ├── postgres-deployment.yaml
    ├── postgres-pvc.yaml
    ├── postgres-service.yaml
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── frontend-deployment.yaml
    ├── frontend-service.yaml
    ├── network-policy.yaml
    └── rbac.yaml
```

## Prerequisites

- Docker Desktop with Kubernetes enabled, OR
- Minikube, OR
- [Kind](https://kind.sigs.k8s.io/docs/user/quick-start#configuring-your-kind-cluster) (RECOMMENDED), OR
- Access to a Kubernetes cluster (EKS, GKE, AKS)
- kubectl CLI installed
- Basic understanding of containers and YAML

## Quick Start

### 1. Clone and Navigate

```bash
git clone https://github.com/yourusername/Learning-Kubernetes-Security.git
cd Learning-Kubernetes-Security
```

### 2. Build Docker Images

**Note**: If you use Podman instead of Docker, you have to start your machine first, like so:

```
podman machine init
podman machine start
```

Check if it works with: `docker version`

Where we have set an alias for Podman in `~/.zshr` or `~/.bashrc` like so:

```
alias docker=podman
alias docker-compose=podman-compose
```

Then reload your shell:

```
source ~/.zshrc  # or ~/.bashrc
```

```bash
cd app/backend
docker build -t secure-notes-backend:v1 .

cd ../frontend
docker build -t secure-notes-frontend:v1 .
```

You will see the images (here: `secure-notes-backend` and `secure-notes-frontend`) listed in Podman's Desktop application.

\*_Note_: Set Up Local Development Cluster

If you don't have a Kubernetes cluster running, you can set up a local development cluster using one of these options:

**Option A: Minikube (Recommended for beginners)**

```bash
# Start minikube
minikube start

# Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

**Option B: Kind (Kubernetes in Docker)**

```bash
# Install kind (if not already installed)
# On macOS: brew install kind
# On Linux: go install sigs.k8s.io/kind@v0.20.0

# Create cluster
kind create cluster --name secure-notes

# Verify cluster
kubectl cluster-info
```

**Option C: Docker Desktop**

- Enable Kubernetes in Docker Desktop settings
- Go to Settings → Kubernetes → Enable Kubernetes
- Click "Apply & Restart"

**Option D: Use existing cluster**
If you have access to a remote cluster, ensure your kubectl context is set correctly:

```bash
# Check current context
kubectl config current-context

# List available contexts
kubectl config get-contexts

# Switch context if needed
kubectl config use-context <your-cluster-context>
```

### 3. Create Namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

### 4. Create Secrets (Update with your values)

```bash
kubectl apply -f k8s/secrets.yaml
```

### 5. Deploy Database

```bash
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml
```

### 6. Deploy Backend API

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
```

### 7. Deploy Frontend

```bash
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
```

### 8. Apply Security Policies

```bash
kubectl apply -f k8s/network-policy.yaml
kubectl apply -f k8s/rbac.yaml
```

### 9. Access the Application

```bash
kubectl port-forward -n secure-notes svc/frontend-service 8080:80
```

Open http://localhost:8080 in your browser.

## Key Learning Points

### Deployments vs Pods

Deployments manage ReplicaSets, which manage Pods. This provides self-healing, rolling updates, and rollback capabilities.

### Service Types

- **ClusterIP**: Internal-only (database, backend API)
- **LoadBalancer**: External access (frontend)
- **NodePort**: Alternative external access method

### ConfigMaps vs Secrets

- ConfigMaps: Non-sensitive configuration (URLs, feature flags)
- Secrets: Sensitive data (passwords, API keys) - base64 encoded

### Network Policies

Default deny-all with explicit allow rules demonstrates zero-trust security principles.

### Security Contexts

- `runAsNonRoot: true`
- `allowPrivilegeEscalation: false`
- `readOnlyRootFilesystem: true` where possible

## Common Commands

```bash
# View all resources in namespace
kubectl get all -n secure-notes

# Check pod logs
kubectl logs -n secure-notes <pod-name>

# Execute command in pod
kubectl exec -it -n secure-notes <pod-name> -- /bin/sh

# View pod details
kubectl describe pod -n secure-notes <pod-name>

# Scale deployment
kubectl scale deployment backend-api -n secure-notes --replicas=3

# View events
kubectl get events -n secure-notes --sort-by='.lastTimestamp'
```

## Testing Network Policies

```bash
# Create a test pod
kubectl run -it --rm debug --image=alpine --restart=Never -n secure-notes -- sh

# Try to connect to backend (should work within namespace)
wget -O- http://backend-service:5000/health

# Try to connect from default namespace (should fail)
kubectl run -it --rm debug --image=alpine --restart=Never -- sh
wget -O- http://backend-service.secure-notes:5000/health
```

## Cleanup

```bash
kubectl delete namespace secure-notes
```

## Next Steps

- Add Ingress controller for proper external routing
- Implement Horizontal Pod Autoscaler (HPA)
- Add Prometheus/Grafana for monitoring
- Implement service mesh (Istio/Linkerd)
- Add security scanning tools (Falco, OPA/Gatekeeper)
- Implement GitOps with ArgoCD or FluxCD

## Security Considerations for Production

1. **Secrets Management**: Use external secret managers (HashiCorp Vault, AWS Secrets Manager)
1. **Image Security**: Scan images for vulnerabilities, use private registries
1. **Pod Security Standards**: Enforce restricted policies
1. **Network Segmentation**: Fine-tune network policies per microservice
1. **RBAC**: Apply principle of least privilege
1. **Audit Logging**: Enable Kubernetes audit logs
1. **Encryption**: Enable encryption at rest and in transit

## Resources

- [Kubernetes Official Documentation](https://kubernetes.io/docs/)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)
- [OWASP Kubernetes Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Kubernetes_Security_Cheat_Sheet.html)

## License

MIT License - Feel free to use this for learning purposes.

---

**Author**: [Your Name] - Cyber Security Engineer  
**Last Updated**: October 2025
