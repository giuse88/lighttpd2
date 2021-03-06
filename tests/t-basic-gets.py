# -*- coding: utf-8 -*-

from base import *
from requests import *

LUA_SHOW_ENV_INFO="""

function show_env_info(vr)
	if vr:handle_direct() then
		vr.resp.status = 200
		vr.resp.headers["Content-Type"] = "text/plain"
		vr.out:add(vr.env["INFO"])
	end
end

actions = show_env_info

"""

class TestSimpleRequest(CurlRequest):
	URL = "/test.txt"
	EXPECT_RESPONSE_BODY = TEST_TXT
	EXPECT_RESPONSE_CODE = 200
	EXPECT_RESPONSE_HEADERS = [("Content-Type", "text/plain; charset=utf-8")]

class TestSimpleRequestStatus(CurlRequest):
	URL = "/test.txt"
	EXPECT_RESPONSE_BODY = TEST_TXT
	EXPECT_RESPONSE_CODE = 403
	config = """
defaultaction;
static_no_fail;
set_status 403;
"""

class TestSimpleRespond(CurlRequest):
	URL = "/test.txt"
	EXPECT_RESPONSE_BODY = "hello"
	EXPECT_RESPONSE_CODE = 200
	config = 'respond "hello";'

class TestIndex1(CurlRequest):
	URL = "/"
	EXPECT_RESPONSE_BODY = TEST_TXT
	EXPECT_RESPONSE_CODE = 200
	config = """
defaultaction;
index "test.txt";
"""

class TestIndex2(CurlRequest):
	URL = "/"
	EXPECT_RESPONSE_BODY = TEST_TXT
	EXPECT_RESPONSE_CODE = 200
	config = """
defaultaction;
index "index.html", "test.txt";
"""

class TestSimpleInfo(CurlRequest):
	URL = "/?a_simple_query"
	EXPECT_RESPONSE_BODY = "a_simple_query"
	EXPECT_RESPONSE_CODE = 200

	config = """
env.set "INFO" => "%{req.query}";
show_env_info;
"""

class TestBadRequest1(CurlRequest):
	# unencoded query
	URL = "/?complicated?query= $"
	EXPECT_RESPONSE_CODE = 400

class TestStaticExcludeExtensions1(CurlRequest):
	URL = "/test.php"
	EXPECT_RESPONSE_CODE = 403
	config = """
defaultaction;
static.exclude_extensions ".php";
"""

class TestStaticExcludeExtensions2(CurlRequest):
	URL = "/test.php"
	EXPECT_RESPONSE_CODE = 403
	config = """
defaultaction;
static.exclude_extensions (".php", ".py");
"""

class TestServerTag(CurlRequest):
	URL = "/test.txt"
	EXPECT_RESPONSE_BODY = TEST_TXT
	EXPECT_RESPONSE_CODE = 200
	EXPECT_RESPONSE_HEADERS = [("Server", "apache - no really!")]
	config = """
defaultaction;
server.tag "apache - no really!";
"""

class TestConditionalHeader1(CurlRequest):
	URL = "/"
	EXPECT_RESPONSE_BODY = "a"
	REQUEST_HEADERS = ["X-Select: a"]
	config = """
if req.header["X-Select"] == "a" {
	respond "a";
} else {
	respond "b";
}
"""

class TestConditionalHeader2(CurlRequest):
	URL = "/"
	EXPECT_RESPONSE_BODY = "b"
	config = """
if req.header["X-Select"] == "a" {
	respond "a";
} else {
	respond "b";
}
"""

class TestSimplePattern1(CurlRequest):
	URL = "/"
	EXPECT_RESPONSE_CODE = 403
	EXPECT_RESPONSE_BODY = "hello"
	REQUEST_HEADERS = ["X-Select: hello"]
	config = """
respond 403 => "%{req.header[X-Select]}";
"""

class ProvideStatus(TestBase):
	runnable = False
	vhost = "status"
	config = """
setup { module_load "mod_status"; }
status.info;
"""

class Test(GroupTest):
	group = [
		TestSimpleRequest,
		TestSimpleRequestStatus,
		TestSimpleRespond,
		TestIndex1,
		TestIndex2,
		TestSimpleInfo,
		TestBadRequest1,
		TestStaticExcludeExtensions1,
		TestStaticExcludeExtensions2,
		TestServerTag,
		TestConditionalHeader1,
		TestConditionalHeader2,
		TestSimplePattern1,
		ProvideStatus
	]

	def Prepare(self):
		self.PrepareFile("www/default/test.txt", TEST_TXT)
		self.PrepareFile("www/default/test.php", "")
		show_env_info_lua = self.PrepareFile("lua/show_env_info.lua", LUA_SHOW_ENV_INFO)
		self.plain_config = """
show_env_info = {{
	lua.handler "{show_env_info_lua}";
}};
""".format(show_env_info_lua = show_env_info_lua)
