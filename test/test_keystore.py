import pytest
# @pytest.mark.skip
# def test_add_1():
# 	assert 100+200 == 400,"failed"

# @pytest.mark.skip
# def test_add_2():
# 	assert 100+200 == 300,"failed"

# @pytest.mark.xfail
# def test_add_3():
# 	assert 15+13 == 28,"failed"

# @pytest.mark.xfail
# def test_add_4():
# 	assert 15+13 == 100,"failed"

# def test_add_5():
# 	assert 3+2 == 5

# def test_add_6():
# 	assert 3+3 == 6,"failed"

import files_client
import keystore

import base64

def test_keystore_good():
	mac='00:21:213312'
	# wrong_mac='00012003:::3'
	master_key=files_client._generate_safe_key(32)
	# wrong_key='npoekey'

	real_file_key=base64.b64encode(files_client._generate_safe_key(32)).decode()

	keystore.set_key('test',mac,master_key,real_file_key)

	key = keystore.get_key('test',mac,master_key)

	assert key == real_file_key

def test_keystore_wrong_master_key():
	mac='00:21:213312'
	wrong_mac='00012003:::3'
	master_key=files_client._generate_safe_key(32)
	wrong_key=files_client._generate_safe_key(32)

	real_file_key=base64.b64encode(files_client._generate_safe_key(32)).decode()

	keystore.set_key('test',mac,master_key,real_file_key)

	key = keystore.get_key('test',mac,wrong_key)

	assert key != real_file_key

def test_keystore_wrong_details():
	mac='00:21:213312'
	wrong_mac='00012003:::3'
	master_key=files_client._generate_safe_key(32)

	real_file_key=base64.b64encode(files_client._generate_safe_key(32)).decode()

	keystore.set_key('test',mac,master_key,real_file_key)
	with pytest.raises(keystore.NoKeyError):
		key = keystore.get_key('test',wrong_mac,master_key)
