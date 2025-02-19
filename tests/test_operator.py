import os
import shutil
import sys

import pytest

from bentoctl.exceptions import OperatorConfigNotFound, OperatorLoadException
from bentoctl.operator import operator as op
from bentoctl.operator.operator import _import_module, Operator


from .conftest import TESTOP_PATH


def test_import_module():
    testop = _import_module("testop", TESTOP_PATH)
    # check if the imported module has the operations delete and update
    assert hasattr(testop, "deploy")
    assert hasattr(testop, "update")

    with pytest.raises(OperatorLoadException):
        testop = _import_module("MODULE_THAT_IS_NOT_PRESENT", TESTOP_PATH)
    # clean the paths in sys.path
    sys.path.pop(0)


def test_operator_class_init(tmp_path, monkeypatch):
    testop_path = tmp_path / "test-operator"
    shutil.copytree(TESTOP_PATH, testop_path)
    operator = Operator(testop_path)
    assert operator.name == "testop"
    assert operator.module_name == "testop"

    with pytest.raises(OperatorConfigNotFound):
        Operator(tmp_path)

    with pytest.raises(OperatorLoadException):

        def raise_error(*_):
            raise OperatorLoadException

        monkeypatch.setattr(op, "_import_module", raise_error)
        Operator(testop_path)


def test_operator_class_operations(tmp_path):
    testop_path = tmp_path / "test-operator"
    shutil.copytree(TESTOP_PATH, testop_path)
    operator = Operator(testop_path)

    deployable_path = operator.deploy("test_bundle", "first", {})
    assert os.path.exists(deployable_path)

    shutil.rmtree(deployable_path)
    deployable_path = operator.update("test_bundle", "second", {})
    assert os.path.exists(deployable_path)
    shutil.rmtree(deployable_path)

    assert operator.describe("third", {}) is not None
    assert operator.delete("forth", {}) is None
