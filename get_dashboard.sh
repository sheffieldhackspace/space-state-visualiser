#!/bin/bash
# get the JSON for a dashboard

# load secrets
source .env

dashboard_id="${1}"
if [[ -z "${dashboard_id}" ]]; then
  echo "no id supplied"
  echo "./get_dashboard.sh <dashboard_id>"
  exit 1
fi

code=$(
  curl -s \
  --request GET \
  -H "Authorization: Bearer ${GRAFANA_API_TOKEN}" \
  -H "Accept: application/json" \
  "${GRAFANA_ROOT_URL}apis/dashboard.grafana.app/v1beta1/namespaces/org-${GRAFANA_ORG}/dashboards/${dashboard_id}" \
  -o /tmp/db19515.tmp \
  -w '%{http_code}'
)

if [[ "${code}" != 200 ]]; then
  echo "bad! got response code ${code} !" >> /dev/stderr
  exit 1
fi

json=$(cat "/tmp/db19515.tmp")

echo "${json}" | jq -r '.metadata | "Got Dashboard!\n  name: \(.name) \n  org: \(.namespace) \n  uid: \(.uid) \nProviding embedded \".spec\" object…"' >> /dev/stderr

echo "${json}" | jq '.spec'

rm /tmp/db19515.tmp
