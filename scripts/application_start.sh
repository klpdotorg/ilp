#!/bin/bash

systemctl restart ilp.service || exit 1
systemctl restart nginx.service || exit 1
