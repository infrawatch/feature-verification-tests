#!/bin/bash
#
# Run the feature verification tests from a workstation.
#
# Usage:
#   ./run_functional_tests_locally.sh [playbook] [extra ansible-playbook args]
#
# Examples:
#   ./run_functional_tests_locally.sh run_verify_metrics_osp18.yml
#   ./run_functional_tests_locally.sh run_verify_metrics_osp18.yml --tags precheck
#   ./run_functional_tests_locally.sh run_graphing_test.yml
#
# Environment:
#   KUBECONFIG    kubeconfig for the cluster under test (default ~/.kube/config)
#   OCP_PASSWORD  OpenShift console password, required by the graphing tests
#   INVENTORY     inventory to use (default ci/inventory/local.yml)
#
set -euo pipefail

cd "$(dirname "$0")"

PLAYBOOK="${1:-run_functional_tests.yml}"
shift || true

export KUBECONFIG="${KUBECONFIG:-$HOME/.kube/config}"
INVENTORY="${INVENTORY:-inventory/local.yml}"

if [ ! -r "$KUBECONFIG" ]; then
    echo "KUBECONFIG $KUBECONFIG is not readable. Log in to the cluster first." >&2
    exit 1
fi

if ! command -v oc >/dev/null 2>&1; then
    echo "oc was not found on PATH." >&2
    exit 1
fi

exec ansible-playbook -i "$INVENTORY" "$PLAYBOOK" "$@"
