from oslo_config import cfg


backend_opts = [
    cfg.StrOpt('region_name', default='HaNoi',
               help='Region Name'),
    cfg.DictOpt("volume_types", default={},
                help="A dict of volume types with format:"
                " volume_type_id: volume_type_name")
]

# nova_api section
nova_api_groups = cfg.OptGroup('nova_api')
nova_api_opts = [
    cfg.StrOpt(
        'db_user',
        default="nova",
        help="Username use to connect database"
    ),
    cfg.StrOpt(
        'db_passwd',
        help="Password use to connect database"),
    cfg.StrOpt(
        'db_host',
        help="Database hostname"
    ),
    cfg.StrOpt(
        'db_name',
        help="Database name"
    )
]

# nova_cell1 section
nova_cell1_groups = cfg.OptGroup('nova_cell1')
nova_cell1_opts = [
    cfg.StrOpt(
        'db_user',
        default="nova",
        help="Username use to connect database"
    ),
    cfg.StrOpt(
        'db_passwd',
        help="Password use to connect database"),
    cfg.StrOpt(
        'db_host',
        help="Database hostname"
    ),
    cfg.StrOpt(
        'db_name',
        help="Database name"
    )
]

# neutron section
neutron_groups = cfg.OptGroup('neutron')
neutron_opts = [
    cfg.StrOpt(
        'db_user',
        default="neutron",
        help="Username use to connect database"
    ),
    cfg.StrOpt(
        'db_passwd',
        help="Password use to connect database"),
    cfg.StrOpt(
        'db_host',
        help="Database hostname"
    ),
    cfg.StrOpt(
        'db_name',
        help="Database name"
    )
]

# cinder section
cinder_groups = cfg.OptGroup('cinder')
cinder_opts = [
    cfg.StrOpt(
        'db_user',
        default="cinder",
        help="Username use to connect database"
    ),
    cfg.StrOpt(
        'db_passwd',
        help="Password use to connect database"),
    cfg.StrOpt(
        'db_host',
        help="Database hostname"
    ),
    cfg.StrOpt(
        'db_name',
        help="Database name"
    )
]


def register_config_option():
    cfg.CONF.register_opts(backend_opts)

    cfg.CONF.register_opts(
        nova_api_opts,
        group=nova_api_groups
    )

    cfg.CONF.register_opts(
        nova_cell1_opts,
        group=nova_cell1_groups
    )

    cfg.CONF.register_opts(
        neutron_opts,
        group=neutron_groups
    )

    cfg.CONF.register_opts(
        cinder_opts,
        group=cinder_groups
    )
