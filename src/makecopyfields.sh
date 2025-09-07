#!/usr/bin/env bash

# for solr as deployed on my laptop
SOLR_CMD=/opt/homebrew/bin/solr

# for solr as deployed on RTL-managed Ubuntu servers
# SOLR_CMD=/opt/solr/bin/solr

SOLR_PORT="8983"

SOLR_CORES="tgtm"

function copy_fields()
{
    # ====================
    # Copy fields
    # ====================

    echo "Making copyFields for $1 $2 ..."
    curl -s -S -X POST -H 'Content-type:application/json' --data-binary "{
      \"add-copy-field\":{
        \"source\": \"$1\",
        \"dest\": [ \"$2\" ]}
    }" $SOLR_CORE_URL/schema
}

for SOLR_CORE in $SOLR_CORES
do
    SOLR_CORE_URL="http://localhost:$SOLR_PORT/solr/$SOLR_CORE"
    SOLR_RELOAD_URL="http://localhost:$SOLR_PORT/solr/admin/cores?action=RELOAD&core=$SOLR_CORE"

    echo "Adding copyfield for $1"
    field_name="$1"
    txt_field_name=${field_name%_*}_txt
    copy_fields $field_name $txt_field_name

    echo "Reloading core ${SOLR_CORE}..."
    curl -s -S "$SOLR_RELOAD_URL"
done

