bash scripts/setup/build-docker-node.sh
bash scripts/setup/deploy-flsim-code.sh
scripts_dir='/tmp/paper-code-flsim-testbed/scripts/node'
ssh scj@svr1.flsim.iovi.com "bash $scripts_dir/launch-svr1-nodes.sh"
ssh scj@svr2.flsim.iovi.com "bash $scripts_dir/launch-svr2-nodes.sh"
ssh scj@svr11.flsim.iovi.com "bash $scripts_dir/launch-svr11-nodes.sh"
ssh scj@svr12.flsim.iovi.com "bash $scripts_dir/launch-svr12-nodes.sh"
ssh scj@svr13.flsim.iovi.com "bash $scripts_dir/launch-svr13-nodes.sh"
ssh scj@svr14.flsim.iovi.com "bash $scripts_dir/launch-svr14-nodes.sh"