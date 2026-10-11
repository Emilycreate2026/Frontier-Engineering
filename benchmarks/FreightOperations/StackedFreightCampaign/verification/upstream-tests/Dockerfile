FROM iregistry.baidu-int.com/lihuaiming/hardco-resource-pool-redeployment-environment@sha256:09311974431df584cc5a0d020f62431551f173dd12696d8346d901bb562d21e8
USER root
RUN rm -rf /app /tests && mkdir -p /app/results /logs/verifier
COPY . /tests/
WORKDIR /app
