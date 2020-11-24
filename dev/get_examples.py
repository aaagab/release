#!/usr/bin/env python3

def get_examples():
    print("""
release --set-conf
release --set-launcher
release --restore
release -i --pgks message prompt
release --update message
release --upgrade message
release --bump-version --increment
release --transfer --from-pkg --to-bin --beta
release --transfer --from-pkg --to-bin
release --transfer --from-pkg --to-rel
release --transfer --from-rel --to-bin ~/mnt/web/bin --pname guidelines
release --transfer --from-rel --to-bin ~/mnt/office-lw-vm/bin --pname guidelines --no-symlink
release --transfer --from-rel --to-rel ~/mnt/office-lw-vm/rel --pname guidelines
release --transfer --from-rel ~/fty/rel --to-rel ~/mnt/office-lw-vm/rel --pname guidelines
release --transfer --from-rel --to-rel ~/mnt/office-lw-vm/rel --pname message --pv 5.0.7
# repair release when developing
cd /home/$USER/fty/wrk/r/release/1/src
/home/$USER/fty/wrk/r/release/1/src/main.py --transfer --from-pkg --to-bin --beta
# restore release from hdd
cd /home/$USER/fty/rel/release/11.1.0/release/main.py
main.py --transfer --from-rel --to-bin --pname release
        """)