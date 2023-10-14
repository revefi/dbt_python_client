from revefi_dbt_client.parser import parse_args_legacy, parse_args_v2


def test_parse_args_legacy():
    argv = 'dbt --token definitely-a-real-token --project_folder /path/to/project/dir'.split(' ')
    args = parse_args_legacy(argv)
    assert args.token == 'definitely-a-real-token'
    assert args.project_folder == '/path/to/project/dir'
    assert args.target_folder is None
    assert args.logs_folder is None

    argv = 'dbt --token definitely-a-real-token --project_folder /path/to/project/dir --target_folder custom_target_dir --logs_folder /path/to/logs/dir'.split(
        ' ')
    args = parse_args_legacy(argv)
    assert args.token == 'definitely-a-real-token'
    assert args.project_folder == '/path/to/project/dir'
    assert args.target_folder == 'custom_target_dir'
    assert args.logs_folder == '/path/to/logs/dir'


def test_parse_args_v2():
    argv = '--token definitely-a-real-token --project_folder /path/to/project/dir'.split(' ')
    args = parse_args_v2(argv)
    assert args.token == 'definitely-a-real-token'
    assert args.project_folder == '/path/to/project/dir'
    assert args.target_folder is None
    assert args.logs_folder is None

    argv = '--token definitely-a-real-token --project_folder /path/to/project/dir --target_folder custom_target_dir --logs_folder /path/to/logs/dir'.split(
        ' ')
    args = parse_args_v2(argv)
    assert args.token == 'definitely-a-real-token'
    assert args.project_folder == '/path/to/project/dir'
    assert args.target_folder == 'custom_target_dir'
    assert args.logs_folder == '/path/to/logs/dir'
