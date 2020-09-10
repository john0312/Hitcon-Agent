#!/bin/bash

scenario=$1

./buildSqfs.sh ./kofserver/diskImages/${scenario}.agent.sqfs ./kofserver/scenario/${scenario}/Extra
