from ...core.devio import interface
from ...core.utils import py3, general


class IStage(interface.IDevice):
    """Generic stage class"""
    _p_direction=interface.EnumParameterClass("direction",[("+",True),(1,True),("-",False),(0,False)])


def muxaxis(*args, **kwargs):
    """Multiplex the function over its axis argument"""
    if len(args)>0:
        return muxaxis(**kwargs)(args[0])
    def ax_func(self, *_, **__):
        return self._mapped_axes
    return general.muxcall("axis",all_arg_func=ax_func,mux_argnames=kwargs.get("mux_argnames",None),return_kind=kwargs.get("return_kind","list"),allow_partial=True)
class IMultiaxisStage(IStage):
    """
    Generic multiaxis stage class.

    Has methods to assign and map axes and the axis device parameter.
    """
    _axes=[]
    _axis_parameter_name="axis"
    def __init__(self):
        super().__init__()
        self._original_axis_parameter=None
        self._mapped_axes=list(self._axes)
        self._add_parameter_class(interface.EnumParameterClass(self._axis_parameter_name,self._axes,alias_case=None,match_prefix=False))
        self._add_info_variable("axes",self.get_all_axes)
    def get_all_axes(self):
        """Get the list of all available axes (taking mapping into account)"""
        return list(self._mapped_axes)
    def _update_axes(self, axes):
        """Update axes list; also removes the axes mapping"""
        self._axes=axes
        self._mapped_axes=axes
        self._replace_parameter_class(interface.EnumParameterClass(self._axis_parameter_name,self._axes,alias_case=None,match_prefix=False))
        self._original_axis_parameter=None
    def remap_axes(self, mapping, accept_original=True):
        """
        Rename axes to the new labels.

        `mapping` is the new axes mapping, which can be a list of new axes name (corresponding to the old axes in order returned by :meth:`get_all_axes`),
        or a dictionary ``{alias: original}`` of the new axes aliases.
        """
        if isinstance(mapping,py3.textstring):
            mapping=list(mapping)
            if len(mapping)!=len(self._axes):
                raise ValueError("number of mapped axes {} is different from the number of the original axes {}".format(mapping,self._axes))
        if isinstance(mapping,(list,tuple)):
            mapping=dict(zip(mapping,self._axes))
        opar=self._original_axis_parameter
        if opar is None:
            self._original_axis_parameter=opar=self._parameters[self._axis_parameter_name]
        wpar=interface.EnumParameterClass(self._axis_parameter_name,mapping,alias_case=None,allowed_alias=("all" if accept_original else "exact"),match_prefix=False)
        self._mapped_axes=[wpar.i(ax) for ax in self._axes]
        self._replace_parameter_class(interface.CombinedParameterClass(self._axis_parameter_name,[wpar,opar]))