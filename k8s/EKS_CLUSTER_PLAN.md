# EKS Cluster Setup Plan with Auto Mode

This plan outlines setting up a new EKS cluster using eksctl with Auto Mode enabled.

## What is EKS Auto Mode?

EKS Auto Mode automates cluster infrastructure management including:
- **Compute**: Automatically provisions and scales nodes
- **Storage**: Manages EBS CSI driver and storage classes
- **Networking**: Handles load balancer controller and VPC CNI

No manual node group management required - EKS handles it all.

## Prerequisites

```bash
# Install eksctl
brew install eksctl

# Verify AWS credentials
aws sts get-caller-identity

# Verify eksctl
eksctl version
```

## Quick Start with Mise Tasks

```bash
# Create the cluster
mise run eks:create

# Deploy everything (CNPG + DB + App)
mise run eks:deploy

# Or deploy individually:
mise run eks:deploy:cnpg   # Install CNPG operator
mise run eks:deploy:db     # Deploy PostgreSQL cluster
mise run eks:deploy:app    # Deploy SDS API
mise run eks:deploy:schema # Run schema migrations
```

## Available Mise Tasks

| Task | Description |
|------|-------------|
| `eks:create` | Create EKS cluster with Auto Mode |
| `eks:delete` | Delete EKS cluster |
| `eks:status` | Check cluster status and nodes |
| `eks:kubeconfig` | Update kubeconfig for the cluster |
| `eks:deploy` | Deploy everything (CNPG + DB + App) |
| `eks:deploy:cnpg` | Install CloudNativePG operator |
| `eks:deploy:db` | Deploy PostgreSQL cluster |
| `eks:deploy:app` | Deploy SDS API |
| `eks:deploy:schema` | Create configmaps and run migrations |

## Manual Steps (if needed)

### Create Cluster

```bash
eksctl create cluster -f k8s/eksctl-cluster.yaml
```

### Verify Cluster

```bash
eksctl get cluster -f k8s/eksctl-cluster.yaml
kubectl get nodes
```

### Delete Cluster

```bash
eksctl delete cluster -f k8s/eksctl-cluster.yaml --wait
```

## Expose the API (Optional)

With Auto Mode, the AWS Load Balancer Controller is automatically managed.

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: hack2future-ingress
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
spec:
  ingressClassName: alb
  rules:
    - http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: hack2future
                port:
                  number: 80
```

```bash
kubectl apply -f k8s/ingress.yaml
kubectl get ingress hack2future-ingress -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

## Directory Structure

```
k8s/
├── eksctl-cluster.yaml    # EKS cluster definition
├── setup-cnpg.sh          # CNPG installation script
├── kind-cluster.yaml      # Local dev cluster (Kind)
├── dev-cluster.yaml       # CNPG PostgreSQL cluster
├── pgschema-update.yaml   # Schema migration job
├── api.yaml               # API deployment
└── EKS_CLUSTER_PLAN.md    # This file
```

## Checklist

- [ ] `mise run eks:create` - Create cluster
- [ ] `mise run eks:deploy:cnpg` - Install CNPG
- [ ] `mise run eks:deploy:db` - Deploy PostgreSQL
- [ ] `mise run eks:deploy:schema` - Run migrations
- [ ] `mise run eks:deploy:app` - Deploy API
- [ ] (Optional) Create ALB ingress
