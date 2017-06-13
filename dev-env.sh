#!/usr/bin/env bash

cleanup() {
	[ -n "${bashrc}" ] && rm -f "${bashrc}"
}

trap cleanup HUP TERM EXIT

topdir=$(readlink -f $(dirname $0))
PYTHON_VERSION=${PYTHON_VERSION:-2.7}
package=$(python${PYTHON_VERSION} ${topdir}/setup.py --name)
bashrc=$(TMPDIR=${topdir} mktemp .devrc-XXXXXX)
make=$(which gmake 2>/dev/null || which make)

if [ -n "${VIRTUAL_ENV}" ]; then
	virtualenv=$(readlink -f ${VIRTUAL_ENV})
else
	virtualenv=${topdir}/virtualenv${PYTHON_VERSION}
fi
venv_devdir=${virtualenv}/${package}-dev

if [ ! -d ${virtualenv} ]; then
	virtualenv --python=python${PYTHON_VERSION} ${virtualenv} || exit 1
fi

# Install requirements
[ ! -d ${venv_devdir} ] && mkdir -p ${venv_devdir}
for req_path in ${topdir}/requirements*.txt; do
	req_basename=$(basename ${req_path})
	req_status=${venv_devdir}/${req_basename}
	if [ ${req_status} -ot ${req_path} ]; then
		(source ${virtualenv}/bin/activate && ${make} -C ${topdir} ${req_basename})
		touch -m ${req_status}
	fi
done

# Instructions to run when entering new shell
cat > ${bashrc} <<-EOF
	[ -f ~/.bash_profile ] && source ~/.bash_profile
	source ${virtualenv}/bin/activate
EOF

# Enter developmet shell
if [ -z "$*" ]; then
	/usr/bin/env bash --rcfile ${bashrc} -i
else
	source ${bashrc}
	$*
fi

# vim: noet
