cd ..

target_dir='/tmp/paper-code-flsim-testbed/'
servers=('svr1.flsim.iovi.com' 'svr2.flsim.iovi.com' 'svr11.flsim.iovi.com' 'svr12.flsim.iovi.com' 'svr13.flsim.iovi.com' 'svr14.flsim.iovi.com' 'dfs1.flsim.iovi.com' 'dfs2.flsim.iovi.com')
for server in "${servers[@]}"
do
    ssh scj@$server "sudo rm -rf $target_dir"
    rsync -avr --exclude '.git' --exclude '*.ipynb' --exclude '*.pyc' --exclude '*.sql' --exclude '*.pkl' \
    --exclude 'backup' --exclude '.vscode' --delete paper-code-flsim-testbed/ scj@$server:$target_dir
done