#!/bin/bash

systemctl start ilp.service || exit 1
systemctl start nginx.service || exit 1
