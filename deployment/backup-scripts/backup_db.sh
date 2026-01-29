#!/bin/bash
docker exec -t deployment_db_1 pg_dump -U admin lab_timetabling_db > backup_$(date +%F).sql
