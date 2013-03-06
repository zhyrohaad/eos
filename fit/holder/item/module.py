#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
#
# This file is part of Eos.
#
# Eos is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Eos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Eos. If not, see <http://www.gnu.org/licenses/>.
#===============================================================================


from eos.const import Location
from eos.fit.holder import MutableAttributeHolder
from .charge import Charge


class Module(MutableAttributeHolder):
    """Ship's module from any slot."""

    __slots__ = ('__charge',)

    def __init__(self, type_):
        MutableAttributeHolder.__init__(self, type_)
        self.__charge = None

    @property
    def _location(self):
        return Location.ship

    @property
    def _other(self):
        """Purely service property, used in fit link tracker registry"""
        return self.charge

    @property
    def charge(self):
        return self.__charge

    @charge.setter
    def charge(self, value):
        oldCharge = self.charge
        if oldCharge is not None:
            if self.fit is not None:
                self.fit._removeHolder(oldCharge)
            self.__charge = None
            oldCharge.container = None
        if value is None:
            return
        if isinstance(value, int):
            type_ = self.fit._eos._cacheHandler.getType(value)
            newCharge = Charge(type_)
        else:
            newCharge = value
        if newCharge is not None:
            newCharge.container = self
            self.__charge = newCharge
            if self.fit is not None:
                self.fit._addHolder(newCharge)