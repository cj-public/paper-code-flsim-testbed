CREATE DATABASE `flsim` /*!40100 DEFAULT CHARACTER SET utf8 */;
use flsim 

CREATE TABLE `blockfl_task_pool` (
`id` varchar(256) PRIMARY KEY,
`publisher_name` varchar(256) NOT NULL,
`model_name` varchar(256) NOT NULL,
`dataset_source` varchar(256) NOT NULL,
`dataset_sharding_schema` varchar(256) NOT NULL,
`evalset_id` varchar(256) NOT NULL,
`init_weights_id` varchar(256) NOT NULL,
`status` varchar(256) NOT NULL,
`max_iteration` int(10) NOT NULL,
`extra` text,
`scheduled_time` timestamp,
`required_flsim_version` varchar(256) NOT NULL,
`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `blockfl_weights_pool` (
`id` varchar(256) PRIMARY KEY,
`hash` varchar(256) NOT NULL,
`task_id` varchar(256) NOT NULL,
`_type` varchar(256) NOT NULL, # local or global weights
`is_aggregated` int(11) NOT NULL, # 0 False, 1 True
`is_trained` int(11) NOT NULL, # 0 False, 1 True
`source_weights_ids` text,
`contributor` varchar(256) NOT NULL,
`contributor_mode` varchar(256),
`performance` text,
`storage_system` varchar(256) NOT NULL,
`access_path` varchar(1024) NOT NULL,
`used_time` text NOT NULL,
`extra` text,
`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
alter table blockfl_weights_pool add index index_blockfl_weights_pool1 (`hash`);
alter table blockfl_weights_pool add index index_blockfl_weights_pool2 (`task_id`);
alter table blockfl_weights_pool add index index_blockfl_weights_pool3 (`create_time`);
alter table blockfl_weights_pool add index index_blockfl_weights_pool4 (`is_aggregated`);
alter table blockfl_weights_pool add index index_blockfl_weights_pool5 (`_type`);

CREATE TABLE `blockfl_weights_global_evaluation` (
`id` varchar(256) PRIMARY KEY,
`task_id` varchar(256) NOT NULL,
`weights_id` varchar(256) NOT NULL,
`dataset_id` varchar(256) NOT NULL,
`evaluator` varchar(256) NOT NULL,
`accuracy` float NOT NULL,
`loss` float NOT NULL,
`used_time` text NOT NULL,
`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
alter table blockfl_weights_global_evaluation add index index_blockfl_weights_global_evaluation1 (`task_id`);
alter table blockfl_weights_global_evaluation add index index_blockfl_weights_global_evaluation2 (`weights_id`);

CREATE TABLE `dagfl_task_pool` (
`id` varchar(256) PRIMARY KEY,
`publisher_name` varchar(256) NOT NULL,
`model_name` varchar(256) NOT NULL,
`dataset_source` varchar(256) NOT NULL,
`dataset_sharding_schema` varchar(256) NOT NULL,
`evalset_id` varchar(256) NOT NULL,
`init_weights_id` varchar(256) NOT NULL,
`status` varchar(256) NOT NULL,
`max_iteration` int(10) NOT NULL,
`extra` text,
`scheduled_time` timestamp,
`required_flsim_version` varchar(256) NOT NULL,
`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `dagfl_weights_pool` (
`id` varchar(256) PRIMARY KEY,
`hash` varchar(256) NOT NULL,
`task_id` varchar(256) NOT NULL,
`_type` varchar(256) NOT NULL, # local or global weights
`is_aggregated` int(11) NOT NULL, # 0 False, 1 True
`is_trained` int(11) NOT NULL, # 0 False, 1 True
`source_weights_ids` text,
`contributor` varchar(256) NOT NULL,
`contributor_mode` varchar(256),
`performance` text,
`storage_system` varchar(256) NOT NULL,
`access_path` varchar(1024) NOT NULL,
`used_time` text NOT NULL,
`extra` text,
`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
alter table dagfl_weights_pool add index index_dagfl_weights_pool1 (`hash`);
alter table dagfl_weights_pool add index index_dagfl_weights_pool2 (`task_id`);
alter table dagfl_weights_pool add index index_dagfl_weights_pool3 (`create_time`);
alter table dagfl_weights_pool add index index_dagfl_weights_pool4 (`is_aggregated`);
alter table dagfl_weights_pool add index index_dagfl_weights_pool5 (`_type`);

CREATE TABLE `dagfl_weights_local_evaluation` (
`id` varchar(256) PRIMARY KEY,
`task_id` varchar(256) NOT NULL,
`weights_id` varchar(256) NOT NULL,
`dataset_id` varchar(256) NOT NULL,
`worker_name` varchar(256) NOT NULL,
`accuracy` float NOT NULL,
`loss` float NOT NULL,
`used_time` text NOT NULL,
`is_aggregated` int(11) DEFAULT 0, # 0 False, 1 True
`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
alter table dagfl_weights_local_evaluation add index index_dagfl_weights_local_evaluation1 (`task_id`);
alter table dagfl_weights_local_evaluation add index index_dagfl_weights_local_evaluation2 (`weights_id`);
alter table dagfl_weights_local_evaluation add index index_dagfl_weights_local_evaluation3 (`dataset_id`);
alter table dagfl_weights_local_evaluation add index index_dagfl_weights_local_evaluation4 (`worker_name`);
alter table dagfl_weights_local_evaluation add index index_dagfl_weights_local_evaluation5 (`accuracy`);
alter table dagfl_weights_local_evaluation add index index_dagfl_weights_local_evaluation6 (`loss`);

CREATE TABLE `dagfl_weights_global_evaluation` (
`id` varchar(256) PRIMARY KEY,
`task_id` varchar(256) NOT NULL,
`weights_id` varchar(256) NOT NULL,
`dataset_id` varchar(256) NOT NULL,
`evaluator` varchar(256) NOT NULL,
`accuracy` float NOT NULL,
`loss` float NOT NULL,
`used_time` text NOT NULL,
`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
alter table dagfl_weights_global_evaluation add index index_dagfl_weights_global_evaluation1 (`task_id`);
alter table dagfl_weights_global_evaluation add index index_dagfl_weights_global_evaluation2 (`weights_id`);

CREATE TABLE `fedasync_task_pool` (
`id` varchar(256) PRIMARY KEY,
`publisher_name` varchar(256) NOT NULL,
`model_name` varchar(256) NOT NULL,
`dataset_source` varchar(256) NOT NULL,
`dataset_sharding_schema` varchar(256) NOT NULL,
`evalset_id` varchar(256) NOT NULL,
`init_weights_id` varchar(256) NOT NULL,
`status` varchar(256) NOT NULL,
`max_iteration` int(10) NOT NULL,
`extra` text,
`scheduled_time` timestamp,
`required_flsim_version` varchar(256) NOT NULL,
`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `fedasync_weights_pool` (
`id` varchar(256) PRIMARY KEY,
`hash` varchar(256) NOT NULL,
`task_id` varchar(256) NOT NULL,
`_type` varchar(256) NOT NULL, # local or global weights
`is_aggregated` int(11) NOT NULL, # 0 False, 1 True
`is_trained` int(11) NOT NULL, # 0 False, 1 True
`source_weights_ids` text,
`contributor` varchar(256) NOT NULL,
`contributor_mode` varchar(256),
`performance` text,
`storage_system` varchar(256) NOT NULL,
`access_path` varchar(1024) NOT NULL,
`used_time` text NOT NULL,
`extra` text,
`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
alter table fedasync_weights_pool add index index_fedasync_weights_pool1 (`hash`);
alter table fedasync_weights_pool add index index_fedasync_weights_pool2 (`task_id`);
alter table fedasync_weights_pool add index index_fedasync_weights_pool3 (`create_time`);
alter table fedasync_weights_pool add index index_fedasync_weights_pool4 (`is_aggregated`);
alter table fedasync_weights_pool add index index_fedasync_weights_pool5 (`_type`);

CREATE TABLE `fedasync_weights_global_evaluation` (
`id` varchar(256) PRIMARY KEY,
`task_id` varchar(256) NOT NULL,
`weights_id` varchar(256) NOT NULL,
`dataset_id` varchar(256) NOT NULL,
`evaluator` varchar(256) NOT NULL,
`accuracy` float NOT NULL,
`loss` float NOT NULL,
`used_time` text NOT NULL,
`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
alter table fedasync_weights_global_evaluation add index index_fedasync_weights_global_evaluation1 (`task_id`);
alter table fedasync_weights_global_evaluation add index index_fedasync_weights_global_evaluation2 (`weights_id`);

CREATE TABLE `fedavg_task_pool` (
`id` varchar(256) PRIMARY KEY,
`publisher_name` varchar(256) NOT NULL,
`model_name` varchar(256) NOT NULL,
`dataset_source` varchar(256) NOT NULL,
`dataset_sharding_schema` varchar(256) NOT NULL,
`evalset_id` varchar(256) NOT NULL,
`init_weights_id` varchar(256) NOT NULL,
`status` varchar(256) NOT NULL,
`max_iteration` int(10) NOT NULL,
`extra` text,
`scheduled_time` timestamp,
`required_flsim_version` varchar(256) NOT NULL,
`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `fedavg_weights_pool` (
`id` varchar(256) PRIMARY KEY,
`hash` varchar(256) NOT NULL,
`task_id` varchar(256) NOT NULL,
`_type` varchar(256) NOT NULL, # local or global weights
`is_aggregated` int(11) NOT NULL, # 0 False, 1 True
`is_trained` int(11) NOT NULL, # 0 False, 1 True
`source_weights_ids` text,
`contributor` varchar(256) NOT NULL,
`contributor_mode` varchar(256),
`performance` text,
`storage_system` varchar(256) NOT NULL,
`access_path` varchar(1024) NOT NULL,
`used_time` text NOT NULL,
`extra` text,
`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
alter table fedavg_weights_pool add index index_fedavg_weights_pool1 (`hash`);
alter table fedavg_weights_pool add index index_fedavg_weights_pool2 (`task_id`);
alter table fedavg_weights_pool add index index_fedavg_weights_pool3 (`create_time`);
alter table fedavg_weights_pool add index index_fedavg_weights_pool4 (`is_aggregated`);
alter table fedavg_weights_pool add index index_fedavg_weights_pool5 (`_type`);

CREATE TABLE `fedavg_weights_global_evaluation` (
`id` varchar(256) PRIMARY KEY,
`task_id` varchar(256) NOT NULL,
`weights_id` varchar(256) NOT NULL,
`dataset_id` varchar(256) NOT NULL,
`evaluator` varchar(256) NOT NULL,
`accuracy` float NOT NULL,
`loss` float NOT NULL,
`used_time` text NOT NULL,
`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
alter table fedavg_weights_global_evaluation add index index_fedavg_weights_global_evaluation1 (`task_id`);
alter table fedavg_weights_global_evaluation add index index_fedavg_weights_global_evaluation2 (`weights_id`);

CREATE TABLE `ironforge_task_pool` (
`id` varchar(256) PRIMARY KEY,
`publisher_name` varchar(256) NOT NULL,
`model_name` varchar(256) NOT NULL,
`dataset_source` varchar(256) NOT NULL,
`dataset_sharding_schema` varchar(256) NOT NULL,
`evalset_id` varchar(256) NOT NULL,
`init_weights_id` varchar(256) NOT NULL,
`status` varchar(256) NOT NULL,
`max_iteration` int(10) NOT NULL,
`extra` text,
`scheduled_time` timestamp,
`required_flsim_version` varchar(256) NOT NULL,
`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `ironforge_weights_pool` (
`id` varchar(256) PRIMARY KEY,
`hash` varchar(256) NOT NULL,
`task_id` varchar(256) NOT NULL,
`_type` varchar(256) NOT NULL, # local or global weights
`is_aggregated` int(11) NOT NULL, # 0 False, 1 True
`is_trained` int(11) NOT NULL, # 0 False, 1 True
`source_weights_ids` text,
`contributor` varchar(256) NOT NULL,
`contributor_mode` varchar(256),
`pol` int(11) DEFAULT 1,
`performance` text,
`storage_system` varchar(256) NOT NULL,
`access_path` varchar(1024) NOT NULL,
`used_time` text NOT NULL,
`extra` text,
`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
alter table ironforge_weights_pool add index index_ironforge_weights_pool1 (`hash`);
alter table ironforge_weights_pool add index index_ironforge_weights_pool2 (`task_id`);
alter table ironforge_weights_pool add index index_ironforge_weights_pool3 (`create_time`);
alter table ironforge_weights_pool add index index_ironforge_weights_pool4 (`is_aggregated`);
alter table ironforge_weights_pool add index index_ironforge_weights_pool5 (`_type`);

CREATE TABLE `ironforge_challenge_pool` (
`id` varchar(256) PRIMARY KEY,
`challenger_id` varchar(256) NOT NULL,
`weights_id` varchar(256) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `ironforge_weights_local_evaluation` (
`id` varchar(256) PRIMARY KEY,
`task_id` varchar(256) NOT NULL,
`weights_id` varchar(256) NOT NULL,
`dataset_id` varchar(256) NOT NULL,
`worker_name` varchar(256) NOT NULL,
`accuracy` float NOT NULL,
`loss` float NOT NULL,
`used_time` text NOT NULL,
`is_aggregated` int(11) DEFAULT 0, # 0 False, 1 True
`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
alter table ironforge_weights_local_evaluation add index index_ironforge_weights_local_evaluation1 (`task_id`);
alter table ironforge_weights_local_evaluation add index index_ironforge_weights_local_evaluation2 (`weights_id`);
alter table ironforge_weights_local_evaluation add index index_ironforge_weights_local_evaluation3 (`dataset_id`);
alter table ironforge_weights_local_evaluation add index index_ironforge_weights_local_evaluation4 (`worker_name`);
alter table ironforge_weights_local_evaluation add index index_ironforge_weights_local_evaluation5 (`accuracy`);
alter table ironforge_weights_local_evaluation add index index_ironforge_weights_local_evaluation6 (`loss`);

CREATE TABLE `ironforge_weights_global_evaluation` (
`id` varchar(256) PRIMARY KEY,
`task_id` varchar(256) NOT NULL,
`weights_id` varchar(256) NOT NULL,
`dataset_id` varchar(256) NOT NULL,
`evaluator` varchar(256) NOT NULL,
`accuracy` float NOT NULL,
`loss` float NOT NULL,
`used_time` text NOT NULL,
`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
alter table ironforge_weights_global_evaluation add index index_ironforge_weights_global_evaluation1 (`task_id`);
alter table ironforge_weights_global_evaluation add index index_ironforge_weights_global_evaluation2 (`weights_id`);

CREATE TABLE `y_datasets` (
`id` varchar(256) PRIMARY KEY,
`shard_id` varchar(256) DEFAULT NULL,
`source` varchar(256) NOT NULL,
`sharding_schema` varchar(256) DEFAULT NULL,
`storage_system` varchar(256) NOT NULL,
`access_path` varchar(1024) NOT NULL,
`_usage` varchar(256) NOT NULL,
`extra` text,
`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `y_runners` (
`name` varchar(256) PRIMARY KEY,
`_type` varchar(256) NOT NULL, # runner type, worker, master or miner
`binded_task_id` varchar(256),
`node_type` varchar(256) NOT NULL,
`node_settings` text NOT NULL,
`extra` text,
`flsim_version` varchar(256),
`activate_time` timestamp,
`running_task_info` text,
`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
alter table y_runners add index index_runners1(`name`);

CREATE TABLE `y_runner_task_settings` (
`task_id` varchar(256),
`fl_system` varchar(256),
`runner_name` varchar(256),
`runner_mode` varchar(256),
`dataset_id` varchar(256),
`runtime_params` text,
`extra` text,
`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (`task_id`, `runner_name`, `fl_system`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `z_diagnose_runner_executation_history` (
`id` INT AUTO_INCREMENT PRIMARY KEY,
`runner_name` varchar(256) NOT NULL,
`fl_system` varchar(256) NOT NULL,
`task_id` varchar(256) NOT NULL,
`start_time` timestamp NOT NULL,
`complete_time` timestamp,
`status` varchar(256) NOT NULL,
`message` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `z_diagnose_runner_runtime_errors` (
`id` INT AUTO_INCREMENT PRIMARY KEY,
`runner_name` varchar(256) NOT NULL,
`fl_system` varchar(256) NOT NULL,
`task_info` text NOT NULL,
`message` text NOT NULL,
`occur_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
alter table z_diagnose_runner_runtime_errors add index index_z_diagnose_runner_runtime_errors1 (`occur_time`);

CREATE TABLE `z_diagnose_slow_dfs_analysis` (
`id` INT AUTO_INCREMENT PRIMARY KEY,
`fl_system` varchar(256) NOT NULL,
`runner_name` varchar(256) NOT NULL,
`_type` varchar(256) NOT NULL,
`status` varchar(256) NOT NULL,
`node_url` varchar(1024) NOT NULL,
`shell_cmd` text NOT NULL,
`std_resp` text,
`err_resp` text,
`used_time` float(13,4) NOT NULL,
`start_time` timestamp NOT NULL,
`complete_time` timestamp NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
alter table z_diagnose_slow_dfs_analysis add index index_z_diagnose_slow_dfs_analysis1 (`start_time`);
alter table z_diagnose_slow_dfs_analysis add index index_z_diagnose_slow_dfs_analysis2 (`used_time`);

CREATE TABLE `z_diagnose_slow_sql_analysis` (
`id` INT AUTO_INCREMENT PRIMARY KEY,
`exec_stack` text NOT NULL,
`sql_content` MEDIUMTEXT NOT NULL,
`used_time` float(13,4) NOT NULL,
`start_time` timestamp NOT NULL,
`complete_time` timestamp NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
alter table z_diagnose_slow_sql_analysis add index index_z_diagnose_slow_sql_analysis1 (`start_time`);
alter table z_diagnose_slow_sql_analysis add index index_z_diagnose_slow_sql_analysis2 (`used_time`);

CREATE TABLE `z_diagnose_task_scheduling_history` (
`id` INT AUTO_INCREMENT PRIMARY KEY,
`fl_system` varchar(256) NOT NULL,
`task_id` varchar(256) NOT NULL,
`event` text NOT NULL,
`occur_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `z_diagnose_whole_tasks_progress` (
`fl_system` varchar(256) NOT NULL,
`task_id` varchar(256) NOT NULL,
`task_status` varchar(256) NOT NULL,
`completed_iteration` int(11) NOT NULL,
`max_iteration` int(11) NOT NULL,
`task_start_time` timestamp,
`latest_update_time` timestamp,
`schedule_priority` int(11) NOT NULL,
`schedule_max_concurrent` int(11) NOT NULL,
`update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY(`fl_system`, `task_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `z_diagnose_wrong_sql` (
`id` INT AUTO_INCREMENT PRIMARY KEY,
`sql_content` text NOT NULL,
`occur_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;