#!/bin/bash

# set the variables in the supervisor environment
sed -i "s/ENV_DEBUG/$DEBUG/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_KAFKA_IP/$KAFKA_IP/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_KAFKA_PORT/$KAFKA_PORT/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_KAFKA_KUBERNETES_TOPIC/$KAFKA_KUBERNETES_TOPIC/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_PROMETHEUS_HOST/$PROMETHEUS_HOST/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_PROMETHEUS_PORT/$PROMETHEUS_PORT/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_PROMETHEUS_POLLING_STEP/$PROMETHEUS_POLLING_STEP/g" /etc/supervisor/supervisord.conf
sed -i "s/ENV_SCHEDULER_SECONDS/$SCHEDULER_SECONDS/g" /etc/supervisor/supervisord.conf

# Restart services
service supervisor start && service supervisor status

# Makes services start on system start
update-rc.d supervisor defaults

echo "Initialization completed."
tail -f /dev/null  # Necessary in order for the container to not stop
