# -*- coding: utf-8 -*-

# To do transfer servers between projects

from flask import Flask
from flask import request
from oslo_config import cfg
from sqlalchemy import create_engine


from loguru import logger


from config import register_config_option


CONF = cfg.CONF
FORMATTIME = "%Y-%m-%dT%H:%M:%SZ"


app = Flask("transfer-servers")


def get_sql_connection(db_info):
    SQL_CONNECTION = "mysql+pymysql://%(db_user)s:%(db_passwd)s\
@%(db_host)s/%(db_name)s" % db_info
    return create_engine(SQL_CONNECTION, echo=True).connect()


def get_flavors(flavor_id):
    try:
        nova_api_conn = get_sql_connection(DB_NOVA_API_INFO)
        query = """
            select name
            from flavors
            where id="%(flavor_id)s"
        """ % {
            "flavor_id": flavor_id
        }

        flavor = nova_api_conn.execute(query).fetchone()
        nova_api_conn.close()
        return flavor.name
    except Exception as e:
        logger.error(e)


def update_instance_mappings(payload):
    try:
        nova_api_conn = get_sql_connection(DB_NOVA_API_INFO)
        query = """
            update instance_mappings
            set project_id = "%(new_project_id)s",
                user_id = "%(new_user_id)s"
            where instance_uuid = "%(server_id)s"
        """ % {
            "server_id": payload.get("server_id"),
            "new_project_id": payload.get("to")["project"]["id"],
            "new_user_id": payload.get("to")["user"]["id"],
        }

        nova_api_conn.execute(query)
        nova_api_conn.close()
    except Exception as e:
        logger.error(e)


def get_block_device_mapping(payload):
    try:
        volume_ids = []
        nova_cell1_conn = get_sql_connection(DB_NOVA_CELL1_INFO)
        query = """
        select volume_id
        from block_device_mapping
        where instance_uuid="%(server_id)s";
        """ % {
            "server_id": payload.get("server_id")
        }

        for volume in nova_cell1_conn.execute(query):
            volume_ids.append(volume.volume_id)

        nova_cell1_conn.close()
        return volume_ids
    except Exception as e:
        logger.error(e)


def update_instance_actions(payload):
    try:
        nova_cell1_conn = get_sql_connection(DB_NOVA_CELL1_INFO)
        query = """
            update instance_actions
            set project_id="%(new_project_id)s",
                user_id="%(new_user_id)s"
            where instance_uuid="%(server_id)s"
        """ % {
            "server_id": payload.get("server_id"),
            "new_project_id": payload.get("to")["project"]["id"],
            "new_user_id": payload.get("to")["user"]["id"],
        }

        nova_cell1_conn.execute(query)
        nova_cell1_conn.close()
    except Exception as e:
        logger.error(e)


def get_instances(payload):
    try:
        nova_cell1_conn = get_sql_connection(DB_NOVA_CELL1_INFO)
        query = """
            select * from instances
            where uuid="%(server_id)s";
        """ % {
            "server_id": payload.get("server_id"),
        }

        result = nova_cell1_conn.execute(query).fetchone()

        informations = {
            "display_name": result.display_name,
            "instance_type": get_flavors(result.instance_type_id),
            "memory_mb": result.memory_mb,
            "vcpus": result.vcpus,
            "vm_state": result.vm_state,
        }
        nova_cell1_conn.close()
        return informations
    except Exception as e:
        logger.error(e)


def update_instances(payload):
    try:
        nova_cell1_conn = get_sql_connection(DB_NOVA_CELL1_INFO)
        query = """
            update instances
            set project_id="%(new_project_id)s",
                user_id="%(new_user_id)s"
            where uuid="%(server_id)s";
        """ % {
            "server_id": payload.get("server_id"),
            "new_project_id": payload.get("to")["project"]["id"],
            "new_user_id": payload.get("to")["user"]["id"],
        }

        nova_cell1_conn.execute(query)
        nova_cell1_conn.close()
    except Exception as e:
        logger.error(e)


def get_instance_metadata(payload):
    # Return list instance metadata
    try:
        metadata = []
        nova_cell1_conn = get_sql_connection(DB_NOVA_CELL1_INFO)
        query = """
            select instance_metadata.key, value
            from instance_metadata
            where instance_uuid="%(server_id)s";
        """ % {
            "server_id": payload.get("server_id"),
        }

        for key, value in nova_cell1_conn.execute(query):
            metadata.append({
                "key": key,
                "value": value
            })

        nova_cell1_conn.close()
        return metadata
    except Exception as e:
        logger.error(e)


def get_virtual_interfaces(payload):
    # Return list port bindings
    ports = []
    nova_cell1_conn = get_sql_connection(DB_NOVA_CELL1_INFO)
    query = """
        select uuid
        from virtual_interfaces
        where instance_uuid="%(server_id)s";
    """ % {
        "server_id": payload.get("server_id"),
    }

    for port in nova_cell1_conn.execute(query):
        ports.append(port.uuid)

    nova_cell1_conn.close()
    return ports


def update_ports(payload, ports):
    neutron_conn = get_sql_connection(DB_NEUTRON_INFO)
    for port in ports:
        query = """
            update ports
            set project_id="%(new_project_id)s"
            where id="%(port_id)s";
        """ % {
            "new_project_id": payload.get("to")["project"]["id"],
            "port_id": port,
        }

        neutron_conn.execute(query)


def get_default_security_group_id(payload):
    security_group_ids = None
    neutron_conn = get_sql_connection(DB_NEUTRON_INFO)
    query = """
            select id
            from securitygroups
            where project_id="%(new_project_id)s"
            and   name="default"
        """ % {
        "new_project_id": payload.get("to")["project"]["id"],
    }

    for securitygroup in neutron_conn.execute(query):
        security_group_ids = securitygroup.id

    neutron_conn.close()
    return security_group_ids


def get_securitygroupportbindings(payload, port):
    neutron_conn = get_sql_connection(DB_NEUTRON_INFO)
    securitygroups = []
    query = """
        select security_group_id
        from securitygroupportbindings
        where port_id="%(port_id)s";
    """ % {
        "port_id": port,
    }

    for securitygroup in neutron_conn.execute(query):
        securitygroups.append(securitygroup.security_group_id)

    neutron_conn.close()
    return securitygroups


def update_securitygroupportbindings(payload, ports, security_group_id):
    try:
        neutron_conn = get_sql_connection(DB_NEUTRON_INFO)
        for port in ports:
            securitygroups = get_securitygroupportbindings(
                payload, port)
            # Update to default security get
            query = """
                    update securitygroupportbindings
                    set    security_group_id="%(security_group_id)s"
                    where port_id="%(port_id)s"
                    and   security_group_id="%(securitygroup)s";
                """ % {
                "port_id": port,
                "securitygroup": securitygroups[0],
                "security_group_id": security_group_id
            }

            neutron_conn.execute(query)

            for securitygroup in securitygroups[1:]:
                # Delete old security group bindings
                query = """
                    delete from securitygroupportbindings
                    where port_id="%(port_id)s"
                    and   security_group_id="%(securitygroup)s";
                """ % {
                    "port_id": port,
                    "securitygroup": securitygroup
                }

                neutron_conn.execute(query)

        neutron_conn.close()
    except Exception as e:
        logger.error(e)


def list_snapshots(volume_id):
    # Return list snapshot of volume_id
    try:
        snapshots = []
        cinder_conn = get_sql_connection(DB_CINDER_INFO)
        query = """
            select id
            from snapshots
            where volume_id="%(volume_id)s"
            and   status!="deleted"
        """ % {
            "volume_id": volume_id,
        }

        for raw in cinder_conn.execute(query):
            snapshots.append(raw.id)

        cinder_conn.close()

        return snapshots
    except Exception as e:
        logger.error(e)


def get_snapshots(snapshot_id):
    try:
        cinder_conn = get_sql_connection(DB_CINDER_INFO)
        query = """
            select *
            from snapshots
            where id="%(snapshot_id)s"
            and   status!="deleted"
        """ % {
            "snapshot_id": snapshot_id,
        }

        result = cinder_conn.execute(query).fetchone()

        informations = {
            "display_name": result.display_name,
            "volume_id": result.volume_id,
            "volume_size": result.volume_size,
            "volume_type_id": result.volume_type_id,
        }
        cinder_conn.close()
        return informations
    except Exception as e:
        logger.error(e)


def update_snapshots(payload, volumes):
    try:
        cinder_conn = get_sql_connection(DB_CINDER_INFO)
        for volume in volumes:
            query = """
                update snapshots
                set project_id="%(new_project_id)s",
                    user_id="%(new_user_id)s"
                where volume_id="%(volume_id)s"
                and   status!="deleted"
            """ % {
                "new_project_id": payload.get("to")["project"]["id"],
                "new_user_id": payload.get("to")["user"]["id"],
                "volume_id": volume,
            }

            cinder_conn.execute(query)
        cinder_conn.close()
    except Exception as e:
        logger.error(e)


def get_snapshot_metadata(snapshot_id):
    # Return list instance metadata
    metadata = []
    cinder_conn = get_sql_connection(DB_CINDER_INFO)
    query = """
        select snapshot_metadata.key, value
        from snapshot_metadata
        where snapshot_id="%(snapshot_id)s";
    """ % {
        "snapshot_id": snapshot_id,
    }

    for key, value in cinder_conn.execute(query):
        metadata.append({
            "key": key,
            "value": value
        })

    cinder_conn.close()
    return metadata


def get_volumes(volume_id):
    try:
        cinder_conn = get_sql_connection(DB_CINDER_INFO)
        query = """
            select *
            from volumes
            where id="%(volume_id)s";
        """ % {
            "volume_id": volume_id,
        }

        volume = cinder_conn.execute(query).fetchone()
        cinder_conn.close()

        return dict(volume)
    except Exception as e:
        logger.error(e)


def update_volumes(payload, volumes):
    try:
        cinder_conn = get_sql_connection(DB_CINDER_INFO)
        for volume in volumes:
            query = """
                update volumes
                set project_id="%(new_project_id)s",
                    user_id="%(new_user_id)s"
                where id="%(volume_id)s";
            """ % {
                "new_project_id": payload.get("to")["project"]["id"],
                "new_user_id": payload.get("to")["user"]["id"],
                "volume_id": volume,
            }

            cinder_conn.execute(query)
        cinder_conn.close()
    except Exception as e:
        logger.error(e)


def get_volume_metadata(volume_id):
    # Return list volume metadata
    metadata = []
    cinder_conn = get_sql_connection(DB_CINDER_INFO)
    query = """
        select volume_metadata.key, value
        from volume_metadata
        where volume_id="%(volume_id)s";
    """ % {
        "volume_id": volume_id,
    }

    for key, value in cinder_conn.execute(query):
        metadata.append({
            "key": key,
            "value": value
        })

    cinder_conn.close()
    return metadata


def get_volume_attachment(volume_id):
    try:
        cinder_conn = get_sql_connection(DB_CINDER_INFO)
        query = """
            select *
            from volume_attachment
            where volume_id="%(volume_id)s";
        """ % {
            "volume_id": volume_id,
        }

        volume = dict(cinder_conn.execute(query).fetchone())
        volume["volume"] = get_volumes(volume_id)

        cinder_conn.close()
        if volume:
            return [volume]
        else:
            return {}
    except Exception as e:
        logger.error(e)


@app.route("/transfer", methods=["post"])
def transfer():
    try:
        payload = request.get_json()

        # Step 1:
        update_instance_mappings(payload)

        # Step 2:
        update_instance_actions(payload)

        # Step 3:
        update_instances(payload)

        # Step 4:
        volumes = get_block_device_mapping(payload)
        update_volumes(payload, volumes)
        update_snapshots(payload, volumes)

        # Step 5:

        # Step 6:

        # Step 7:
        ports = get_virtual_interfaces(payload)

        # Step 8:
        update_ports(payload, ports)

        # Step 9:
        default_security_groups = get_default_security_group_id(payload)
        if default_security_groups:
            update_securitygroupportbindings(
                payload, ports, default_security_groups)

        return {
            "successes": True
        }
    except Exception as e:
        logger.error(e)
        return {
            "successes": False
        }


if __name__ == '__main__':
    cfg.CONF(project='transfer', prog='transfer-servers')
    register_config_option()

    DB_NOVA_API_INFO = {
        'db_user': CONF.nova_api.db_user,
        'db_passwd': CONF.nova_api.db_passwd,
        'db_host': CONF.nova_api.db_host,
        'db_name': CONF.nova_api.db_name,
    }

    DB_NOVA_CELL1_INFO = {
        'db_user': CONF.nova_cell1.db_user,
        'db_passwd': CONF.nova_cell1.db_passwd,
        'db_host': CONF.nova_cell1.db_host,
        'db_name': CONF.nova_cell1.db_name,
    }
    DB_NEUTRON_INFO = {
        'db_user': CONF.neutron.db_user,
        'db_passwd': CONF.neutron.db_passwd,
        'db_host': CONF.neutron.db_host,
        'db_name': CONF.neutron.db_name,
    }
    DB_CINDER_INFO = {
        'db_user': CONF.cinder.db_user,
        'db_passwd': CONF.cinder.db_passwd,
        'db_host': CONF.cinder.db_host,
        'db_name': CONF.cinder.db_name,
    }

    app.run(debug=True)
