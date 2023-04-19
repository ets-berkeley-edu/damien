# Copy Damien data from prod to a test environment

Real-world data, from production, in a test environment promotes effective testing.

## Pull data from production

```
./scripts/bugenhagen/pull_prod_data.sh -d db_connection
```

### Available options
```
-d  Database connection information in the form 'host:port:database:username'
```
### Fun facts about _pull-data.sh_

* CSV files are written to the _scripts/bugenhagen/csv_files directory.

## Push data to test environment

```
./scripts/bugenhagen/push_prod_data.sh -d db_connection
```

### Available options
```
-d  Database connection information in the form 'host:port:database:username'
```
