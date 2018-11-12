#!/bin/bash

sudo systemctl stop ka.service || exit 1
sudo systemctl stop od.service || exit 1
sudo systemctl stop jk.service || exit 1

