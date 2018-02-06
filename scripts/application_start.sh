#!/bin/bash

systemctl start ka.service || exit 1
systemctl start od.service || exit 1
systemctl start nginx.service || exit 1
