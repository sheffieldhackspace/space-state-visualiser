#!/bin/bash
# get the JSON for a dashboard

# load secrets
source .env

dashboard_id="${1}"
if [[ -z "${dashboard_id}" ]]; then
  echo "no id supplied"  >> /dev/stderr
  echo "./get_dashboard.sh <dashboard_id>"  >> /dev/stderr
  exit 1
fi

REQUEST_URL="${GRAFANA_ROOT_URL}apis/dashboard.grafana.app/v1beta1/namespaces/org-${GRAFANA_ORG}/dashboards/${dashboard_id}"
echo "making request to ${REQUEST_URL}…"  >> /dev/stderr

code=$(
  curl -s \
  --request GET \
  -H "Authorization: Bearer ${GRAFANA_API_TOKEN}" \
  -H "Accept: application/json" \
  "${REQUEST_URL}" \
  -o /tmp/db19515.tmp \
  -w '%{http_code}'
)

if [[ "${code}" != 200 ]]; then
  echo "bad! got response code ${code} !" >> /dev/stderr
  echo "error:"  >> /dev/stderr
  cat /tmp/db19515.tmp  >> /dev/stderr
  rm /tmp/db19515.tmp
  exit 1
fi

json=$(cat "/tmp/db19515.tmp")

echo "Got Dashboard! metadata:" >> /dev/stderr
echo "${json}" | jq -r '.metadata' >> /dev/stderr
echo 'Providing embedded ".spec" object…' >> /dev/stderr

echo "${json}" | jq '.spec'

rm /tmp/db19515.tmp
