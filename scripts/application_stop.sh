#!/bin/bash

systemctl stop ka.service || exit 1
systemctl stop od.service || exit 1
