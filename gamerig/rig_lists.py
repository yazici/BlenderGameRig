#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#======================= END GPL LICENSE BLOCK ========================

import os

from . import utils


def get_rig_list(path):
    """ Recursively searches for rig types, and returns a list.
    """
    rigs_dict = dict()
    rigs = []
    implementation_rigs = []
    riguitemplates = {}
    MODULE_DIR = os.path.dirname(__file__)
    RIG_DIR_ABS = os.path.join(MODULE_DIR, utils.RIG_DIR)
    SEARCH_DIR_ABS = os.path.join(RIG_DIR_ABS, path)
    files = os.listdir(SEARCH_DIR_ABS)
    files.sort()

    for f in files:
        is_dir = os.path.isdir(os.path.join(SEARCH_DIR_ABS, f))  # Whether the file is a directory

        # Stop cases
        if f[0] in [".", "_"]:
            continue
        if f.count(".") >= 2 or (is_dir and "." in f):
            print("Warning: %r, filename contains a '.', skipping" % os.path.join(SEARCH_DIR_ABS, f))
            continue

        if is_dir:
            # Check directories
            module_name = os.path.join(path, f).replace(os.sep, ".")
            rig = utils.get_rig_type(module_name)
            # Check if it's a rig itself
            if hasattr(rig, "Rig"):
                rigs.append(f)
            else:
                # Check for sub-rigs
                sub_dict = get_rig_list(os.path.join(path, f, ""))  # "" adds a final slash
                rigs.extend(["%s.%s" % (f, l) for l in sub_dict['rig_list']])
                implementation_rigs.extend(["%s.%s" % (f, l) for l in sub_dict['implementation_rigs']])
                riguitemplates.update(sub_dict['uitemplates'])
        elif f.endswith(".py"):
            # Check straight-up python files
            t = f[:-3]
            module_name = os.path.join(path, t).replace(os.sep, ".")
            rig = utils.get_rig_type(module_name)
            if hasattr(rig, "Rig"):
                rigs.append(t)
            elif hasattr(rig, "UI_TEMPLATE"):
                if hasattr(rig, "UI_LABEL_TEXT") and rig.UI_LABEL_TEXT:
                    if len(rig.UI_LABEL_TEXT) > 1:
                        riguitemplates[module_name] = [rig.UI_TEMPLATE, rig.UI_LABEL_TEXT[0], rig.UI_LABEL_TEXT[1]]
                    else:
                        riguitemplates[module_name] = [rig.UI_TEMPLATE, rig.UI_LABEL_TEXT[0], '']
                else:
                    riguitemplates[module_name] = [rig.UI_TEMPLATE, module_name, '']
            if hasattr(rig, 'IMPLEMENTATION') and rig.IMPLEMENTATION:
                implementation_rigs.append(t)
    rigs.sort()

    rigs_dict['rig_list'] = rigs
    rigs_dict['implementation_rigs'] = implementation_rigs
    rigs_dict['uitemplates'] = riguitemplates

    return rigs_dict


def get_collection_list(rig_list):
    collection_list = []
    for r in rig_list:
        a = r.split(".")
        if len(a) >= 2 and a[0] not in collection_list:
            collection_list.append(a[0])
    return collection_list


# Public variables
rigs_dict = get_rig_list("")
rig_list = rigs_dict['rig_list']
implementation_rigs = rigs_dict['implementation_rigs']
collection_list = get_collection_list(rig_list)
col_enum_list = [("All", "All", ""), ("None", "None", "")] + [(c, c, "") for c in collection_list]
riguitemplate_dic = rigs_dict['uitemplates']
rig_ui_template_enum_list = [("Built in", "Built in", "GameRig Built in Rig UI Template")] + [(k, v[1], v[2]) for k, v in riguitemplate_dic.items()]
#print('riguitemplate_dic = %s' % riguitemplate_dic.keys())
#print('rig_ui_template_enum_list = %s' % rig_ui_template_enum_list)
