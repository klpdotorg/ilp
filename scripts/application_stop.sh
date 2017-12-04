#!/bin/bash

systemctl stop nginx.service || exit 1
systemctl stop ilp.service || exit 1
