scripts_dir='/tmp/paper-code-flsim-testbed/scripts/runner'
ssh scj@svr1.flsim.iovi.com "bash $scripts_dir/destroy-runners.sh"
ssh scj@svr2.flsim.iovi.com "bash $scripts_dir/destroy-runners.sh"
ssh scj@svr11.flsim.iovi.com "bash $scripts_dir/destroy-runners.sh"
ssh scj@svr12.flsim.iovi.com "bash $scripts_dir/destroy-runners.sh"
ssh scj@svr13.flsim.iovi.com "bash $scripts_dir/destroy-runners.sh"
ssh scj@svr14.flsim.iovi.com "bash $scripts_dir/destroy-runners.sh"