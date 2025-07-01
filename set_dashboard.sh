#!/bin/bash
# get the JSON for a dashboard

set -eo pipefail

# load secrets
source .env

dashboard_id="${1}"
if [[ -z "${dashboard_id}" ]]; then
  echo "no id supplied"  >> /dev/stderr
  echo "  output | ./set_dashboard.sh <dashboard_id>"  >> /dev/stderr
  echo "    …or"  >> /dev/stderr
  echo "  ./set_dashboard.sh <dashboard_id> <json_filename>"  >> /dev/stderr
  exit 1
fi

filename="${2}"
if [[ -z "${filename}" ]]; then
  echo "getting json from stdin" >> /dev/stderr
  dashboard_json=$(cat /dev/stdin)
else
  echo "getting json from ${filename}" >> /dev/stderr
  dashboard_json=$(cat "${filename}")
fi

echo "creating json…" >> /dev/stderr

request_json=$(
  jq -n \
    --argjson dashboardjson "${dashboard_json}" \
    --arg dashboard_id "${dashboard_id}" \
    '{}
    | .spec = $dashboardjson
    | .metadata.name = $dashboard_id
    | .metadata.annotations."grafana.app/message" = "automatic API update"
    '
)

echo "making request…" >> /dev/stderr

code=$(
  curl -s \
    --request PUT \
    -H "Authorization: Bearer ${GRAFANA_API_TOKEN}" \
    -H "Content-type: application/json" \
    "${GRAFANA_ROOT_URL}apis/dashboard.grafana.app/v1beta1/namespaces/org-${GRAFANA_ORG}/dashboards/${dashboard_id}" \
    -o /tmp/db12tgy3.tmp \
    -w '%{http_code}' \
    --data "${request_json}"
)

if [[ "${code}" != 200 ]]; then
  echo "bad! got response code ${code} !" >> /dev/stderr
  echo "error:"  >> /dev/stderr
  cat /tmp/db12tgy3.tmp  >> /dev/stderr
  rm /tmp/db12tgy3.tmp
  exit 1
fi

echo "looks like everything went ok!" >> /dev/stderr
echo "you should probably run:"  >> /dev/stderr
echo "./get_dashboard.sh ${dashboard_id} > dashboard.json"


rm /tmp/db12tgy3.tmp
