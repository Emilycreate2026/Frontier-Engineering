FROM iregistry.baidu-int.com/lihuaiming/fpga-scratch-feasibility@sha256:1141f3063dd1686ab5d75e171c5af8a278769edbcd64e122b5d151b558f38a3f
USER root
RUN rm -rf /app && mkdir -p /app/results
COPY . /app/
WORKDIR /app
