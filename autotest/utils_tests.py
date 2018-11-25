import os
if not os.path.exists("temp"):
    os.mkdir("temp")

def add_pi_obj_func_test():
    import os
    import pyemu

    pst = os.path.join("utils","dewater_pest.pst")
    pst = pyemu.optimization.add_pi_obj_func(pst,out_pst_name=os.path.join("temp","dewater_pest.piobj.pst"))
    print(pst.prior_information.loc["pi_obj_func","equation"])
    #pst._update_control_section()
    assert pst.control_data.nprior == 1


def fac2real_test():
    import os
    import numpy as np
    import pyemu
    # pp_file = os.path.join("utils","points1.dat")
    # factors_file = os.path.join("utils","factors1.dat")
    # pyemu.utils.gw_utils.fac2real(pp_file,factors_file,
    #                               out_file=os.path.join("utils","test.ref"))

    pp_file = os.path.join("utils", "points2.dat")
    factors_file = os.path.join("utils", "factors2.dat")
    pyemu.geostats.fac2real(pp_file, factors_file,
                                  out_file=os.path.join("temp", "test.ref"))
    arr1 = np.loadtxt(os.path.join("utils","fac2real_points2.ref"))
    arr2 = np.loadtxt(os.path.join("temp","test.ref"))

    #print(np.nansum(np.abs(arr1-arr2)))
    #print(np.nanmax(np.abs(arr1-arr2)))
    nmax = np.nanmax(np.abs(arr1-arr2))
    assert nmax < 0.01

    # import matplotlib.pyplot as plt
    # diff = (arr1-arr2)/arr1 * 100.0
    # diff[np.isnan(arr1)] = np.nan
    # p = plt.imshow(diff,interpolation='n')
    # plt.colorbar(p)
    # plt.show()

def vario_test():
    import numpy as np
    import pyemu
    contribution = 0.1
    a = 2.0
    for const in [pyemu.utils.geostats.ExpVario,pyemu.utils.geostats.GauVario,
                  pyemu.utils.geostats.SphVario]:

        v = const(contribution,a)
        h = v._h_function(np.array([0.0]))
        assert h == contribution
        h = v._h_function(np.array([a*1000]))
        assert h == 0.0

        v2 = const(contribution,a,anisotropy=2.0,bearing=90.0)
        print(v2._h_function(np.array([a])))


def aniso_test():

    import pyemu
    contribution = 0.1
    a = 2.0
    for const in [pyemu.utils.geostats.ExpVario,pyemu.utils.geostats.GauVario,
                  pyemu.utils.geostats.SphVario]:

        v = const(contribution,a)
        v2 = const(contribution,a,anisotropy=2.0,bearing=90.0)
        v3 = const(contribution,a,anisotropy=2.0,bearing=0.0)
        pt0 = (0,0)
        pt1 = (1,0)
        assert v.covariance(pt0,pt1) == v2.covariance(pt0,pt1)

        pt0 = (0,0)
        pt1 = (0,1)
        assert v.covariance(pt0,pt1) == v3.covariance(pt0,pt1)


def geostruct_test():
    import pyemu
    v1 = pyemu.utils.geostats.ExpVario(0.1,2.0)
    v2 = pyemu.utils.geostats.GauVario(0.1,2.0)
    v3 = pyemu.utils.geostats.SphVario(0.1,2.0)

    g = pyemu.utils.geostats.GeoStruct(0.2,[v1,v2,v3])
    pt0 = (0,0)
    pt1 = (0,0)
    print(g.covariance(pt0,pt1))
    assert g.covariance(pt0,pt1) == 0.5

    pt0 = (0,0)
    pt1 = (1.0e+10,0)
    assert g.covariance(pt0,pt1) == 0.2


def struct_file_test():
    import os
    import pyemu
    structs = pyemu.utils.geostats.read_struct_file(
            os.path.join("utils","struct.dat"))
    #print(structs[0])
    pt0 = (0,0)
    pt1 = (0,0)
    for s in structs:
        assert s.covariance(pt0,pt1) == s.nugget + \
                                             s.variograms[0].contribution
    with open(os.path.join("utils","struct_out.dat"),'w') as f:
        for s in structs:
            s.to_struct_file(f)
    structs1 = pyemu.utils.geostats.read_struct_file(
            os.path.join("utils","struct_out.dat"))
    for s in structs1:
        assert s.covariance(pt0,pt1) == s.nugget + \
                                             s.variograms[0].contribution


def covariance_matrix_test():
    import os
    import pandas as pd
    import pyemu

    pts = pd.read_csv(os.path.join("utils","points1.dat"),delim_whitespace=True,
                      header=None,names=["name","x","y"],usecols=[0,1,2])
    struct = pyemu.utils.geostats.read_struct_file(
            os.path.join("utils","struct.dat"))[0]
    struct.variograms[0].covariance_matrix(pts.x,pts.y,names=pts.name)

    print(struct.covariance_matrix(pts.x,pts.y,names=pts.name).x)


def setup_ppcov_simple():
    import os
    import platform

    exe_file = os.path.join("utils","ppcov.exe")
    print(platform.platform())
    if not os.path.exists(exe_file) or not platform.platform().lower().startswith("win"):
        print("can't run ppcov setup")
        return
    pts_file = os.path.join("utils","points1_test.dat")
    str_file = os.path.join("utils","struct_test.dat")

    args1 = [pts_file,'0.0',str_file,"struct1",os.path.join("utils","ppcov.struct1.out"),'','']
    args2 = [pts_file,'0.0',str_file,"struct2",os.path.join("utils","ppcov.struct2.out"),'','']
    args3 = [pts_file,'0.0',str_file,"struct3",os.path.join("utils","ppcov.struct3.out"),'','']


    for args in [args1,args2,args3]:
        in_file = os.path.join("utils","ppcov.in")
        with open(in_file,'w') as f:
            f.write('\n'.join(args))
        os.system(exe_file + '<' + in_file)


def ppcov_simple_test():
    import os
    import numpy as np
    import pandas as pd
    import pyemu

    pts_file = os.path.join("utils","points1_test.dat")
    str_file = os.path.join("utils","struct_test.dat")

    mat1_file = os.path.join("utils","ppcov.struct1.out")
    mat2_file = os.path.join("utils","ppcov.struct2.out")
    mat3_file = os.path.join("utils","ppcov.struct3.out")

    ppc_mat1 = pyemu.Cov.from_ascii(mat1_file)
    ppc_mat2 = pyemu.Cov.from_ascii(mat2_file)
    ppc_mat3 = pyemu.Cov.from_ascii(mat3_file)

    pts = pd.read_csv(pts_file,header=None,names=["name","x","y"],usecols=[0,1,2],
                      delim_whitespace=True)

    struct1,struct2,struct3 = pyemu.utils.geostats.read_struct_file(str_file)
    print(struct1)
    print(struct2)
    print(struct3)

    for mat,struct in zip([ppc_mat1,ppc_mat2,ppc_mat3],[struct1,struct2,struct3]):

        str_mat = struct.covariance_matrix(x=pts.x,y=pts.y,names=pts.name)
        print(str_mat.row_names)
        delt = mat.x - str_mat.x
        assert np.abs(delt).max() < 1.0e-7



def ppcov_simple_sparse_test():
    import os
    import numpy as np
    import pandas as pd
    import pyemu

    pts_file = os.path.join("utils","points1_test.dat")
    str_file = os.path.join("utils","struct_test.dat")

    mat1_file = os.path.join("utils","ppcov.struct1.out")
    mat2_file = os.path.join("utils","ppcov.struct2.out")
    mat3_file = os.path.join("utils","ppcov.struct3.out")

    ppc_mat1 = pyemu.Cov.from_ascii(mat1_file)
    ppc_mat2 = pyemu.Cov.from_ascii(mat2_file)
    ppc_mat3 = pyemu.Cov.from_ascii(mat3_file)

    pts = pd.read_csv(pts_file,header=None,names=["name","x","y"],usecols=[0,1,2],
                      delim_whitespace=True)

    struct1,struct2,struct3 = pyemu.utils.geostats.read_struct_file(str_file)
    print(struct1)
    print(struct2)
    print(struct3)

    for mat,struct in zip([ppc_mat1,ppc_mat2,ppc_mat3],[struct1,struct2,struct3]):

        str_mat = struct.sparse_covariance_matrix(x=pts.x,y=pts.y,names=pts.name)
        str_mat1 = str_mat.to_matrix()
        delt = mat.x - str_mat1.x
        print(delt)
        assert np.abs(delt).max() < 1.0e-7

def setup_ppcov_complex():
    import os
    import platform

    exe_file = os.path.join("utils","ppcov.exe")
    print(platform.platform())
    if not os.path.exists(exe_file) or not platform.platform().lower().startswith("win"):
        print("can't run ppcov setup")
        return
    pts_file = os.path.join("utils","points1_test.dat")
    str_file = os.path.join("utils","struct_complex.dat")

    args1 = [pts_file,'0.0',str_file,"struct1",os.path.join("utils","ppcov.complex.struct1.out"),'','']
    args2 = [pts_file,'0.0',str_file,"struct2",os.path.join("utils","ppcov.complex.struct2.out"),'','']

    for args in [args1,args2]:
        in_file = os.path.join("utils","ppcov.in")
        with open(in_file,'w') as f:
            f.write('\n'.join(args))
        os.system(exe_file + '<' + in_file)


def ppcov_complex_test():
    import os
    import numpy as np
    import pandas as pd
    import pyemu

    pts_file = os.path.join("utils","points1_test.dat")
    str_file = os.path.join("utils","struct_complex.dat")

    mat1_file = os.path.join("utils","ppcov.complex.struct1.out")
    mat2_file = os.path.join("utils","ppcov.complex.struct2.out")

    ppc_mat1 = pyemu.Cov.from_ascii(mat1_file)
    ppc_mat2 = pyemu.Cov.from_ascii(mat2_file)

    pts = pd.read_csv(pts_file,header=None,names=["name","x","y"],usecols=[0,1,2],
                      delim_whitespace=True)

    struct1,struct2 = pyemu.utils.geostats.read_struct_file(str_file)
    print(struct1)
    print(struct2)

    for mat,struct in zip([ppc_mat1,ppc_mat2],[struct1,struct2]):

        str_mat = struct.covariance_matrix(x=pts.x,y=pts.y,names=pts.name)
        delt = mat.x - str_mat.x
        print(mat.x[:,0])
        print(str_mat.x[:,0])


        print(np.abs(delt).max())

        assert np.abs(delt).max() < 1.0e-7
        #break


def ppcov_complex_sparse_test():
    import os
    import numpy as np
    import pandas as pd
    import pyemu

    pts_file = os.path.join("utils","points1_test.dat")
    str_file = os.path.join("utils","struct_complex.dat")

    mat1_file = os.path.join("utils","ppcov.complex.struct1.out")
    mat2_file = os.path.join("utils","ppcov.complex.struct2.out")

    ppc_mat1 = pyemu.Cov.from_ascii(mat1_file)
    ppc_mat2 = pyemu.Cov.from_ascii(mat2_file)

    pts = pd.read_csv(pts_file,header=None,names=["name","x","y"],usecols=[0,1,2],
                      delim_whitespace=True)

    struct1,struct2 = pyemu.utils.geostats.read_struct_file(str_file)
    print(struct1)
    print(struct2)

    for mat,struct in zip([ppc_mat1,ppc_mat2],[struct1,struct2]):

        str_mat = struct.sparse_covariance_matrix(x=pts.x,y=pts.y,names=pts.name)
        str_mat1 = str_mat.to_matrix()
        delt = mat.x - str_mat1.x
        print(mat.x)
        print(str_mat1.x)
        print(delt)


        print(np.abs(delt).max())

        assert np.abs(delt).max() < 1.0e-7
        #break

def pp_to_tpl_test():
    import os
    import pyemu
    pp_file = os.path.join("utils","points1.dat")
    pp_df = pyemu.gw_utils.pilot_points_to_tpl(pp_file,name_prefix="test_")
    print(pp_df.columns)


def tpl_to_dataframe_test():
    import os
    import pyemu
    pp_file = os.path.join("utils","points1.dat")
    pp_df = pyemu.gw_utils.pilot_points_to_tpl(pp_file,name_prefix="test_")
    df_tpl = pyemu.gw_utils.pp_tpl_to_dataframe(pp_file+".tpl")
    assert df_tpl.shape[0] == pp_df.shape[0]

# def to_mps_test():
#     import os
#     import pyemu
#     jco_file = os.path.join("utils","dewater_pest.jcb")
#     jco = pyemu.Jco.from_binary(jco_file)
#     #print(jco.x)
#     pst = pyemu.Pst(jco_file.replace(".jcb",".pst"))
#     #print(pst.nnz_obs_names)
#     oc_dict = {oc:"l" for oc in pst.nnz_obs_names}
#     obj_func = {name:1.0 for name in pst.par_names}
#
#     #pyemu.optimization.to_mps(jco=jco_file)
#     #pyemu.optimization.to_mps(jco=jco_file,obs_constraint_sense=oc_dict)
#     #pyemu.optimization.to_mps(jco=jco_file,obj_func="h00_00")
#     decision_var_names = pst.parameter_data.loc[pst.parameter_data.pargp=="q","parnme"].tolist()
#     pyemu.optimization.to_mps(jco=jco_file,obj_func=obj_func,decision_var_names=decision_var_names,
#                               risk=0.975)

def setup_pp_test():
    import os
    import pyemu
    try:
        import flopy
    except:
        return
    model_ws = os.path.join("..","examples","Freyberg","extra_crispy")
    ml = flopy.modflow.Modflow.load("freyberg.nam",model_ws=model_ws,check=False)

    pp_dir = os.path.join("utils")
    #ml.export(os.path.join("temp","test_unrot_grid.shp"))

    par_info_unrot = pyemu.pp_utils.setup_pilotpoints_grid(sr=ml.sr, prefix_dict={0: "hk1",1:"hk2"},
                                                           every_n_cell=2, pp_dir=pp_dir, tpl_dir=pp_dir,
                                                           shapename=os.path.join("temp", "test_unrot.shp"),
                                                           )
    #print(par_info_unrot.parnme.value_counts())
    gs = pyemu.geostats.GeoStruct(variograms=pyemu.geostats.ExpVario(a=1000,contribution=1.0))
    ok = pyemu.geostats.OrdinaryKrige(gs,par_info_unrot)
    ok.calc_factors_grid(ml.sr)
    par_info_unrot = pyemu.pp_utils.setup_pilotpoints_grid(sr=ml.sr, prefix_dict={0: ["hk1_", "sy1_", "rch_"]},
                                                           every_n_cell=2, pp_dir=pp_dir, tpl_dir=pp_dir,
                                                           shapename=os.path.join("temp", "test_unrot.shp"),
                                                           )
    ok = pyemu.geostats.OrdinaryKrige(gs, par_info_unrot)
    ok.calc_factors_grid(ml.sr)

    par_info_unrot = pyemu.pp_utils.setup_pilotpoints_grid(ml,prefix_dict={0:["hk1_","sy1_","rch_"]},
                                                     every_n_cell=2,pp_dir=pp_dir,tpl_dir=pp_dir,
                                                     shapename=os.path.join("temp","test_unrot.shp"))
    ok = pyemu.geostats.OrdinaryKrige(gs, par_info_unrot)
    ok.calc_factors_grid(ml.sr)



    ml.sr.rotation = 15
    #ml.export(os.path.join("temp","test_rot_grid.shp"))

    #pyemu.gw_utils.setup_pilotpoints_grid(ml)

    par_info_rot = pyemu.pp_utils.setup_pilotpoints_grid(ml,every_n_cell=2, pp_dir=pp_dir, tpl_dir=pp_dir,
                                                     shapename=os.path.join("temp", "test_rot.shp"))
    ok = pyemu.geostats.OrdinaryKrige(gs, par_info_unrot)
    ok.calc_factors_grid(ml.sr)
    print(par_info_unrot.x)
    print(par_info_rot.x)


def read_hob_test():
    import os
    import pyemu
    hob_file = os.path.join("utils","HOB.txt")
    pyemu.gw_utils.modflow_hob_to_instruction_file(hob_file)


def read_pval_test():
    import os
    import pyemu
    pval_file = os.path.join("utils", "meras_trEnhance.pval")
    pyemu.gw_utils.modflow_pval_to_template_file(pval_file)


def pp_to_shapefile_test():
    import os
    import pyemu
    try:
        import shapefile
    except:
        print("no pyshp")
        return
    pp_file = os.path.join("utils","points1.dat")
    shp_file = os.path.join("temp","points1.dat.shp")
    pyemu.pp_utils.write_pp_shapfile(pp_file)

def write_tpl_test():
    import os
    import pyemu
    tpl_file = os.path.join("utils","test_write.tpl")
    in_file = os.path.join("temp","tpl_test.dat")
    par_vals = {"q{0}".format(i+1):12345678.90123456 for i in range(7)}
    pyemu.pst_utils.write_to_template(par_vals,tpl_file,in_file)


def read_pestpp_runstorage_file_test():
    import os
    import pyemu
    rnj_file = os.path.join("utils","freyberg.rnj")
    #rnj_file = os.path.join("..", "..", "verification", "10par_xsec", "master_opt1","pest.rnj")
    p1,o1 = pyemu.helpers.read_pestpp_runstorage(rnj_file)
    p2,o2 = pyemu.helpers.read_pestpp_runstorage(rnj_file,9)
    diff = p1 - p2
    diff.sort_values("parval1",inplace=True)

def smp_to_ins_test():
    import os
    import pyemu
    smp = os.path.join("utils","TWDB_wells.smp")
    ins = os.path.join('temp',"test.ins")
    try:
        pyemu.pst_utils.smp_to_ins(smp,ins)
    except:
        pass
    else:
        raise Exception("should have failed")
    pyemu.smp_utils.smp_to_ins(smp,ins,True)

def master_and_slaves():
    import shutil
    import pyemu
    slave_dir = os.path.join("..","verification","10par_xsec","template_mac")
    master_dir = os.path.join("temp","master")
    if not os.path.exists(master_dir):
        os.mkdir(master_dir)
    assert os.path.exists(slave_dir)
    pyemu.helpers.start_slaves(slave_dir,"pestpp","pest.pst",1,
                               slave_root="temp",master_dir=master_dir)

    #now try it from within the master dir
    base_cwd = os.getcwd()
    os.chdir(master_dir)
    pyemu.helpers.start_slaves(os.path.join("..","..",slave_dir),
                              "pestpp","pest.pst",3,
                              master_dir='.')
    os.chdir(base_cwd)


def first_order_pearson_regul_test():
    import os
    from pyemu import Schur
    from pyemu.utils.helpers import first_order_pearson_tikhonov,zero_order_tikhonov
    w_dir = "la"
    sc = Schur(jco=os.path.join(w_dir,"pest.jcb"))
    pt = sc.posterior_parameter
    zero_order_tikhonov(sc.pst)
    first_order_pearson_tikhonov(sc.pst,pt,reset=False)

    print(sc.pst.prior_information)
    sc.pst.rectify_pi()
    assert sc.pst.control_data.pestmode == "regularization"
    sc.pst.write(os.path.join('temp','test.pst'))

def zero_order_regul_test():
    import os
    import pyemu
    pst = pyemu.Pst(os.path.join("pst","inctest.pst"))
    pyemu.helpers.zero_order_tikhonov(pst)
    print(pst.prior_information)
    assert pst.control_data.pestmode == "regularization"
    pst.write(os.path.join('temp','test.pst'))

    pyemu.helpers.zero_order_tikhonov(pst,reset=False)
    assert pst.prior_information.shape[0] == pst.npar_adj * 2



def  kl_test():
    import os
    import numpy as np
    import pandas as pd
    import pyemu
    import matplotlib.pyplot as plt
    try:
        import flopy
    except:
        print("flopy not imported...")
        return
    model_ws = os.path.join("..","verification","Freyberg","extra_crispy")
    ml = flopy.modflow.Modflow.load("freyberg.nam",model_ws=model_ws,check=False)
    str_file = os.path.join("..","verification","Freyberg","structure.dat")
    arr_tru = np.loadtxt(os.path.join("..","verification",
                                                 "Freyberg","extra_crispy",
                                                 "hk.truth.ref")) + 20
    basis_file = os.path.join("utils","basis.jco")
    tpl_file = os.path.join("utils","test.tpl")
    factors_file = os.path.join("temp","factors.dat")
    num_eig = 100
    prefixes = ["hk1"]
    df = pyemu.utils.helpers.kl_setup(num_eig=num_eig, sr=ml.sr,
                                             struct=str_file,
                                             factors_file=factors_file,
                                             basis_file=basis_file,
                                            prefixes=prefixes,islog=False)

    basis = pyemu.Matrix.from_binary(basis_file)
    basis = basis[:,:num_eig]
    arr_tru = np.atleast_2d(arr_tru.flatten()).transpose()
    proj = np.dot(basis.T.x,arr_tru)[:num_eig]
    #proj.autoalign = False
    back = np.dot(basis.x, proj)

    back = back.reshape(ml.nrow,ml.ncol)
    df.parval1 = proj
    arr = pyemu.geostats.fac2real(df,factors_file,out_file=None)
    fig = plt.figure(figsize=(10, 10))
    ax1, ax2 = plt.subplot(121),plt.subplot(122)
    mn,mx = arr_tru.min(),arr_tru.max()
    print(arr.max(), arr.min())
    print(back.max(),back.min())
    diff = np.abs(back - arr)
    print(diff.max())
    assert diff.max() < 1.0e-5



def ok_test():
    import os
    import pandas as pd
    import pyemu
    str_file = os.path.join("utils","struct_test.dat")
    pts_data = pd.DataFrame({"x":[1.0,2.0,3.0],"y":[0.,0.,0.],"name":["p1","p2","p3"]})
    gs = pyemu.utils.geostats.read_struct_file(str_file)[0]
    ok = pyemu.utils.geostats.OrdinaryKrige(gs,pts_data)
    interp_points = pts_data.copy()
    kf = ok.calc_factors(interp_points.x,interp_points.y)
    #for ptname in pts_data.name:
    for i in kf.index:
        assert len(kf.loc[i,"inames"])== 1
        assert kf.loc[i,"ifacts"][0] == 1.0
        assert sum(kf.loc[i,"ifacts"]) == 1.0
    print(kf)

def ok_grid_test():

    try:
        import flopy
    except:
        return

    import numpy as np
    import pandas as pd
    import pyemu
    nrow,ncol = 10,5
    delr = np.ones((ncol)) * 1.0/float(ncol)
    delc = np.ones((nrow)) * 1.0/float(nrow)

    num_pts = 0
    ptx = np.random.random(num_pts)
    pty = np.random.random(num_pts)
    ptname = ["p{0}".format(i) for i in range(num_pts)]
    pts_data = pd.DataFrame({"x":ptx,"y":pty,"name":ptname})
    pts_data.index = pts_data.name
    pts_data = pts_data.loc[:,["x","y","name"]]


    sr = flopy.utils.SpatialReference(delr=delr,delc=delc)
    pts_data.loc["i0j0", :] = [sr.xcentergrid[0,0],sr.ycentergrid[0,0],"i0j0"]
    pts_data.loc["imxjmx", :] = [sr.xcentergrid[-1, -1], sr.ycentergrid[-1, -1], "imxjmx"]
    str_file = os.path.join("utils","struct_test.dat")
    gs = pyemu.utils.geostats.read_struct_file(str_file)[0]
    ok = pyemu.utils.geostats.OrdinaryKrige(gs,pts_data)
    kf = ok.calc_factors_grid(sr,verbose=False,var_filename=os.path.join("temp","test_var.ref"),minpts_interp=1)
    ok.to_grid_factors_file(os.path.join("temp","test.fac"))

def ok_grid_zone_test():

    try:
        import flopy
    except:
        return

    import numpy as np
    import pandas as pd
    import pyemu
    nrow,ncol = 10,5
    delr = np.ones((ncol)) * 1.0/float(ncol)
    delc = np.ones((nrow)) * 1.0/float(nrow)

    num_pts = 0
    ptx = np.random.random(num_pts)
    pty = np.random.random(num_pts)
    ptname = ["p{0}".format(i) for i in range(num_pts)]
    pts_data = pd.DataFrame({"x":ptx,"y":pty,"name":ptname})
    pts_data.index = pts_data.name
    pts_data = pts_data.loc[:,["x","y","name"]]


    sr = flopy.utils.SpatialReference(delr=delr,delc=delc)
    pts_data.loc["i0j0", :] = [sr.xcentergrid[0,0],sr.ycentergrid[0,0],"i0j0"]
    pts_data.loc["imxjmx", :] = [sr.xcentergrid[-1, -1], sr.ycentergrid[-1, -1], "imxjmx"]
    pts_data.loc[:,"zone"] = 1
    pts_data.zone.iloc[1] = 2
    print(pts_data.zone.unique())
    str_file = os.path.join("utils","struct_test.dat")
    gs = pyemu.utils.geostats.read_struct_file(str_file)[0]
    ok = pyemu.utils.geostats.OrdinaryKrige(gs,pts_data)
    zone_array = np.ones((nrow,ncol))
    zone_array[0,0] = 2
    kf = ok.calc_factors_grid(sr,verbose=False,
                              var_filename=os.path.join("temp","test_var.ref"),
                              minpts_interp=1,zone_array=zone_array)
    ok.to_grid_factors_file(os.path.join("temp","test.fac"))


def ppk2fac_verf_test():
    import os
    import numpy as np
    import pyemu
    try:
        import flopy
    except:
        return
    ws = os.path.join("..","verification","Freyberg")
    gspc_file = os.path.join(ws,"grid.spc")
    pp_file = os.path.join(ws,"pp_00_pp.dat")
    str_file = os.path.join(ws,"structure.complex.dat")
    ppk2fac_facfile = os.path.join(ws,"ppk2fac_fac.dat")
    pyemu_facfile = os.path.join("temp","pyemu_facfile.dat")
    sr = flopy.utils.SpatialReference.from_gridspec(gspc_file)
    ok = pyemu.utils.OrdinaryKrige(str_file,pp_file)
    ok.calc_factors_grid(sr,maxpts_interp=10)
    ok.to_grid_factors_file(pyemu_facfile)
    zone_arr = np.loadtxt(os.path.join(ws,"extra_crispy","ref","ibound.ref"))

    pyemu_arr = pyemu.utils.fac2real(pp_file,pyemu_facfile,out_file=None)
    ppk2fac_arr = pyemu.utils.fac2real(pp_file,ppk2fac_facfile,out_file=None)
    pyemu_arr[zone_arr == 0] = np.NaN
    pyemu_arr[zone_arr == -1] = np.NaN
    ppk2fac_arr[zone_arr == 0] = np.NaN
    ppk2fac_arr[zone_arr == -1] = np.NaN

    diff = np.abs(pyemu_arr - ppk2fac_arr)
    print(diff)

    assert np.nansum(diff) < 1.0e-6,np.nansum(diff)
    


# def opt_obs_worth():
#     import os
#     import pyemu
#     wdir = os.path.join("utils")
#     os.chdir(wdir)
#     pst = pyemu.Pst(os.path.join("supply2_pest.fosm.pst"))
#     zero_weight_names = [n for n,w in zip(pst.observation_data.obsnme,pst.observation_data.weight) if w == 0.0]
#     #print(zero_weight_names)
#     #for attr in ["base_jacobian","hotstart_resfile"]:
#     #    pst.pestpp_options[attr] = os.path.join(wdir,pst.pestpp_options[attr])
#     #pst.template_files = [os.path.join(wdir,f) for f in pst.template_files]
#     #pst.instruction_files = [os.path.join(wdir,f) for f in pst.instruction_files]
#     #print(pst.template_files)
#     df = pyemu.optimization.get_added_obs_importance(pst,obslist_dict={"zeros":zero_weight_names})
#     os.chdir("..")
#     print(df)


def mflist_budget_test():
    import pyemu
    import os
    try:
        import flopy
    except:
        print("no flopy...")
        return
    model_ws = os.path.join("..","examples","Freyberg_transient")
    ml = flopy.modflow.Modflow.load("freyberg.nam",model_ws=model_ws,check=False,load_only=[])
    list_filename = os.path.join(model_ws,"freyberg.list")
    assert os.path.exists(list_filename)
    df = pyemu.gw_utils.setup_mflist_budget_obs(list_filename,start_datetime=ml.start_datetime)
    print(df)

def mtlist_budget_test():
    import pyemu
    import os
    try:
        import flopy
    except:
        print("no flopy...")
        return
    list_filename = os.path.join("utils","mt3d.list")
    assert os.path.exists(list_filename)
    frun_line,ins_files, df = pyemu.gw_utils.setup_mtlist_budget_obs(list_filename,start_datetime='1-1-1970')
    assert len(ins_files) == 2

    frun_line,ins_files, df = pyemu.gw_utils.setup_mtlist_budget_obs(list_filename,start_datetime='1-1-1970',
                                                                     gw_prefix='')
    assert len(ins_files) == 2

    frun_line, ins_files, df = pyemu.gw_utils.setup_mtlist_budget_obs(list_filename, start_datetime=None)
    assert len(ins_files) == 2



def geostat_prior_builder_test():
    import os
    import numpy as np
    import pyemu
    pst_file = os.path.join("pst","pest.pst")
    pst = pyemu.Pst(pst_file)
    # print(pst.parameter_data)
    tpl_file = os.path.join("utils", "pp_locs.tpl")
    str_file = os.path.join("utils", "structure.dat")


    cov = pyemu.helpers.geostatistical_prior_builder(pst_file,{str_file:tpl_file})
    d1 = np.diag(cov.x)


    df = pyemu.gw_utils.pp_tpl_to_dataframe(tpl_file)
    df.loc[:,"zone"] = np.arange(df.shape[0])
    gs = pyemu.geostats.read_struct_file(str_file)
    cov = pyemu.helpers.geostatistical_prior_builder(pst_file,{gs:df},
                                               sigma_range=4)
    nnz = np.count_nonzero(cov.x)
    assert nnz == pst.npar_adj
    d2 = np.diag(cov.x)
    assert np.array_equiv(d1, d2)

    pst.parameter_data.loc[pst.par_names[1:10], "partrans"] = "tied"
    pst.parameter_data.loc[pst.par_names[1:10], "partied"] = pst.par_names[0]
    cov = pyemu.helpers.geostatistical_prior_builder(pst, {gs: df},
                                                     sigma_range=4)
    nnz = np.count_nonzero(cov.x)
    assert nnz == pst.npar_adj


    ttpl_file = os.path.join("temp", "temp.dat.tpl")
    with open(ttpl_file, 'w') as f:
        f.write("ptf ~\n ~ temp1  ~\n")
    pst.add_parameters(ttpl_file, ttpl_file.replace(".tpl", ""))

    pst.parameter_data.loc["temp1", "parubnd"] = 1.1
    pst.parameter_data.loc["temp1", "parlbnd"] = 0.9

    cov = pyemu.helpers.geostatistical_prior_builder(pst, {str_file: tpl_file})
    assert cov.shape[0] == pst.npar_adj

    scov = pyemu.helpers.sparse_geostatistical_prior_builder(pst,{str_file: tpl_file}).to_matrix()
    d = (cov - scov).x
    #print(d)
    print(d.max())


def geostat_draws_test():
    import os
    import numpy as np
    import pyemu
    pst_file = os.path.join("pst","pest.pst")
    pst = pyemu.Pst(pst_file)
    print(pst.parameter_data)
    tpl_file = os.path.join("utils", "pp_locs.tpl")
    str_file = os.path.join("utils", "structure.dat")


    pe = pyemu.helpers.geostatistical_draws(pst_file,{str_file:tpl_file})
    assert (pe.shape == pe.dropna().shape)

    pst.parameter_data.loc[pst.par_names[1:10], "partrans"] = "tied"
    pst.parameter_data.loc[pst.par_names[1:10], "partied"] = pst.par_names[0]
    pe = pyemu.helpers.geostatistical_draws(pst, {str_file: tpl_file})
    assert (pe.shape == pe.dropna().shape)

    df = pyemu.gw_utils.pp_tpl_to_dataframe(tpl_file)
    df.loc[:,"zone"] = np.arange(df.shape[0])
    gs = pyemu.geostats.read_struct_file(str_file)
    pe = pyemu.helpers.geostatistical_draws(pst_file,{gs:df},
                                          sigma_range=4)

    ttpl_file = os.path.join("temp", "temp.dat.tpl")
    with open(ttpl_file, 'w') as f:
        f.write("ptf ~\n ~ temp1  ~\n")
    pst.add_parameters(ttpl_file, ttpl_file.replace(".tpl", ""))

    pst.parameter_data.loc["temp1", "parubnd"] = 1.1
    pst.parameter_data.loc["temp1", "parlbnd"] = 0.9
    pst.parameter_data.loc[pst.par_names[1:10],"partrans"] = "tied"
    pst.parameter_data.loc[pst.par_names[1:10], "partied"] = pst.par_names[0]
    pe = pyemu.helpers.geostatistical_draws(pst, {str_file: tpl_file})
    assert (pe.shape == pe.dropna().shape)




# def linearuniversal_krige_test():
#     try:
#         import flopy
#     except:
#         return
#
#     import numpy as np
#     import pandas as pd
#     import pyemu
#     nrow,ncol = 10,5
#     delr = np.ones((ncol)) * 1.0/float(ncol)
#     delc = np.ones((nrow)) * 1.0/float(nrow)
#
#     num_pts = 0
#     ptx = np.random.random(num_pts)
#     pty = np.random.random(num_pts)
#     ptname = ["p{0}".format(i) for i in range(num_pts)]
#     pts_data = pd.DataFrame({"x":ptx,"y":pty,"name":ptname})
#     pts_data.index = pts_data.name
#     pts_data = pts_data.loc[:,["x","y","name"]]
#
#
#     sr = flopy.utils.SpatialReference(delr=delr,delc=delc)
#     pts_data.loc["i0j0", :] = [sr.xcentergrid[0,0],sr.ycentergrid[0,0],"i0j0"]
#     pts_data.loc["imxjmx", :] = [sr.xcentergrid[-1, -1], sr.ycentergrid[-1, -1], "imxjmx"]
#     pts_data.loc["i0j0","value"] = 1.0
#     pts_data.loc["imxjmx","value"] = 0.0
#
#     str_file = os.path.join("utils","struct_test.dat")
#     gs = pyemu.utils.geostats.read_struct_file(str_file)[0]
#     luk = pyemu.utils.geostats.LinearUniversalKrige(gs,pts_data)
#     df = luk.estimate_grid(sr,verbose=True,
#                                var_filename=os.path.join("utils","test_var.ref"),
#                                minpts_interp=1)

def gslib_2_dataframe_test():
    import os
    import pyemu
    gslib_file = os.path.join("utils","ch91pt.shp.gslib")
    df = pyemu.geostats.gslib_2_dataframe(gslib_file)
    print(df)

def sgems_to_geostruct_test():
    import os
    import pyemu
    xml_file = os.path.join("utils", "ch00")
    gs = pyemu.geostats.read_sgems_variogram_xml(xml_file)

def load_sgems_expvar_test():
    import os
    import numpy as np
    #import matplotlib.pyplot as plt
    import pyemu
    dfs = pyemu.geostats.load_sgems_exp_var(os.path.join("utils","ch00_expvar"))
    xmn,xmx = 1.0e+10,-1.0e+10
    for d,df in dfs.items():
        xmn = min(xmn,df.x.min())
        xmx = max(xmx,df.x.max())

    xml_file = os.path.join("utils", "ch00")
    gs = pyemu.geostats.read_sgems_variogram_xml(xml_file)
    v = gs.variograms[0]
    #ax = gs.plot(ls="--")
    #plt.show()
    #x = np.linspace(xmn,xmx,100)
    #y = v.inv_h(x)

    #
    #plt.plot(x,y)
    #plt.show()

def read_hydmod_test():
    import os
    import numpy as np
    import pandas as pd
    import pyemu
    try:
        import flopy
    except:
        return
    df, outfile = pyemu.gw_utils.modflow_read_hydmod_file(os.path.join('utils','freyberg.hyd.bin'),
                                                          os.path.join('temp','freyberg.hyd.bin.dat'))
    df = pd.read_csv(os.path.join('temp', 'freyberg.hyd.bin.dat'), delim_whitespace=True)
    dftrue = pd.read_csv(os.path.join('utils', 'freyberg.hyd.bin.dat.true'), delim_whitespace=True)

    assert np.allclose(df.obsval.values, dftrue.obsval.values)

def make_hydmod_insfile_test():
    import os
    import shutil
    import pyemu
    try:
        import flopy
    except:
        return
    shutil.copy2(os.path.join('utils','freyberg.hyd.bin'),os.path.join('temp','freyberg.hyd.bin'))
    pyemu.gw_utils.modflow_hydmod_to_instruction_file(os.path.join('temp','freyberg.hyd.bin'))

    #assert open(os.path.join('utils','freyberg.hyd.bin.dat.ins'),'r').read() == open('freyberg.hyd.dat.ins', 'r').read()
    assert os.path.exists(os.path.join('temp','freyberg.hyd.bin.dat.ins'))

def plot_summary_test():
    import os
    import pandas as pd

    import pyemu
    try:
        import matplotlib.pyplot as plt
    except:
        return

    par_df = pd.read_csv(os.path.join("utils","freyberg_pp.par.usum.csv"),
                         index_col=0)
    idx = list(par_df.index.map(lambda x: x.startswith("HK")))
    par_df = par_df.loc[idx,:]
    ax = pyemu.helpers.plot_summary_distributions(par_df,label_post=True)
    plt.savefig(os.path.join("temp","hk_par.png"))
    plt.close()

    df = os.path.join("utils","freyberg_pp.pred.usum.csv")
    figs,axes = pyemu.helpers.plot_summary_distributions(df,subplots=True)
    #plt.show()
    for i,fig in enumerate(figs):
        plt.figure(fig.number)
        plt.savefig(os.path.join("temp","test_pred_{0}.png".format(i)))
        plt.close(fig)
    df = os.path.join("utils","freyberg_pp.par.usum.csv")
    figs, axes = pyemu.helpers.plot_summary_distributions(df,subplots=True)
    for i,fig in enumerate(figs):
        plt.figure(fig.number)
        plt.savefig(os.path.join("temp","test_par_{0}.png".format(i)))
        plt.close(fig)


def hds_timeseries_test():
    import os
    import shutil
    import numpy as np
    import pandas as pd
    try:
        import flopy
    except:
        return
    import pyemu

    model_ws =os.path.join("..","examples","Freyberg_transient")
    org_hds_file = os.path.join(model_ws, "freyberg.hds")
    hds_file = os.path.join("temp", "freyberg.hds")
    shutil.copy2(org_hds_file, hds_file)
    kij_dict = {"test1":[0,0,0],"test2":(1,1,1)}

    pyemu.gw_utils.setup_hds_timeseries(hds_file,kij_dict,include_path=True)
    pyemu.gw_utils.setup_hds_timeseries(hds_file, kij_dict, include_path=True,prefix="hds")

    m = flopy.modflow.Modflow.load("freyberg.nam",model_ws=model_ws,load_only=[],check=False)
    pyemu.gw_utils.setup_hds_timeseries(hds_file, kij_dict,model=m,include_path=True)
    pyemu.gw_utils.setup_hds_timeseries(hds_file, kij_dict, model=m, include_path=True,prefix="hds")

    org_hds_file = os.path.join("utils", "MT3D001.UCN")
    hds_file = os.path.join("temp", "MT3D001.UCN")
    shutil.copy2(org_hds_file, hds_file)
    kij_dict = {"test1": [0, 0, 0], "test2": (1, 1, 1)}

    pyemu.gw_utils.setup_hds_timeseries(hds_file, kij_dict, include_path=True)
    pyemu.gw_utils.setup_hds_timeseries(hds_file, kij_dict, include_path=True, prefix="hds")

    m = flopy.modflow.Modflow.load("freyberg.nam", model_ws=model_ws, load_only=[], check=False)
    pyemu.gw_utils.setup_hds_timeseries(hds_file, kij_dict, model=m, include_path=True)
    pyemu.gw_utils.setup_hds_timeseries(hds_file, kij_dict, model=m, include_path=True, prefix="hds")

    # df1 = pd.read_csv(out_file, delim_whitespace=True)
    # pyemu.gw_utils.apply_hds_obs(hds_file)
    # df2 = pd.read_csv(out_file, delim_whitespace=True)
    # diff = df1.obsval - df2.obsval


def grid_obs_test():
    import os
    import shutil
    import numpy as np
    import pandas as pd
    try:
        import flopy
    except:
        return
    import pyemu

    m_ws = os.path.join("..", "examples", "freyberg_sfr_update")
    org_hds_file = os.path.join("..","examples","Freyberg_Truth","freyberg.hds")
    org_multlay_hds_file = os.path.join(m_ws, "freyberg.hds")  # 3 layer version
    org_ucn_file = os.path.join(m_ws, "MT3D001.UCN")  # mt example
    hds_file = os.path.join("temp","freyberg.hds")
    multlay_hds_file = os.path.join("temp", "freyberg_3lay.hds")
    ucn_file = os.path.join("temp", "MT3D001.UCN")
    out_file = hds_file+".dat"
    multlay_out_file = multlay_hds_file+".dat"
    ucn_out_file = ucn_file+".dat"
    shutil.copy2(org_hds_file,hds_file)
    shutil.copy2(org_multlay_hds_file, multlay_hds_file)
    shutil.copy2(org_ucn_file, ucn_file)

    pyemu.gw_utils.setup_hds_obs(hds_file)
    df1 = pd.read_csv(out_file,delim_whitespace=True)
    pyemu.gw_utils.apply_hds_obs(hds_file)
    df2 = pd.read_csv(out_file,delim_whitespace=True)
    diff = df1.obsval - df2.obsval
    assert abs(diff.max()) < 1.0e-6, abs(diff.max())

    pyemu.gw_utils.setup_hds_obs(multlay_hds_file)
    df1 = pd.read_csv(multlay_out_file,delim_whitespace=True)
    assert len(df1) == 3*len(df2), "{} != 3*{}".format(len(df1), len(df2))
    pyemu.gw_utils.apply_hds_obs(multlay_hds_file)
    df2 = pd.read_csv(multlay_out_file,delim_whitespace=True)
    diff = df1.obsval - df2.obsval
    assert np.allclose(df1.obsval,df2.obsval), abs(diff.max())

    pyemu.gw_utils.setup_hds_obs(hds_file,skip=-999)
    df1 = pd.read_csv(out_file,delim_whitespace=True)
    pyemu.gw_utils.apply_hds_obs(hds_file)
    df2 = pd.read_csv(out_file,delim_whitespace=True)
    diff = df1.obsval - df2.obsval
    assert diff.max() < 1.0e-6

    pyemu.gw_utils.setup_hds_obs(ucn_file, skip=1.e30, prefix='ucn')
    df1 = pd.read_csv(ucn_out_file, delim_whitespace=True)
    pyemu.gw_utils.apply_hds_obs(ucn_file)
    df2 = pd.read_csv(ucn_out_file, delim_whitespace=True)
    diff = df1.obsval - df2.obsval
    assert np.allclose(df1.obsval, df2.obsval), abs(diff.max())

    # skip = lambda x : x < -888.0
    skip = lambda x: x if x > -888.0 else np.NaN
    pyemu.gw_utils.setup_hds_obs(hds_file,skip=skip)
    df1 = pd.read_csv(out_file,delim_whitespace=True)
    pyemu.gw_utils.apply_hds_obs(hds_file)
    df2 = pd.read_csv(out_file,delim_whitespace=True)
    diff = df1.obsval - df2.obsval
    assert diff.max() < 1.0e-6

    kperk_pairs = (0,0)
    pyemu.gw_utils.setup_hds_obs(hds_file,kperk_pairs=kperk_pairs,
                                 skip=skip)
    df1 = pd.read_csv(out_file,delim_whitespace=True)
    pyemu.gw_utils.apply_hds_obs(hds_file)
    df2 = pd.read_csv(out_file,delim_whitespace=True)
    diff = df1.obsval - df2.obsval
    assert diff.max() < 1.0e-6

    kperk_pairs = [(0, 0), (0, 1), (0, 2)]
    pyemu.gw_utils.setup_hds_obs(multlay_hds_file, kperk_pairs=kperk_pairs,
                                 skip=skip)
    df1 = pd.read_csv(multlay_out_file, delim_whitespace=True)
    assert len(df1) == 3*len(df2), "{} != 3*{}".format(len(df1), len(df2))
    pyemu.gw_utils.apply_hds_obs(multlay_hds_file)
    df2 = pd.read_csv(multlay_out_file, delim_whitespace=True)
    diff = df1.obsval - df2.obsval
    assert np.allclose(df1.obsval, df2.obsval), abs(diff.max())

    kperk_pairs = [(0, 0), (0, 1), (0, 2), (2, 0), (2, 1), (2, 2)]
    pyemu.gw_utils.setup_hds_obs(multlay_hds_file, kperk_pairs=kperk_pairs,
                                 skip=skip)
    df1 = pd.read_csv(multlay_out_file, delim_whitespace=True)
    assert len(df1) == 2 * len(df2), "{} != 2*{}".format(len(df1), len(df2))
    pyemu.gw_utils.apply_hds_obs(multlay_hds_file)
    df2 = pd.read_csv(multlay_out_file, delim_whitespace=True)
    diff = df1.obsval - df2.obsval
    assert np.allclose(df1.obsval, df2.obsval), abs(diff.max())

    m = flopy.modflow.Modflow.load("freyberg.nam", model_ws=m_ws, load_only=["BAS6"],forgive=False,verbose=True)
    kperk_pairs = [(0, 0), (0, 1), (0, 2)]
    skipmask = m.bas6.ibound.array
    pyemu.gw_utils.setup_hds_obs(multlay_hds_file, kperk_pairs=kperk_pairs,
                                 skip=skipmask)
    df1 = pd.read_csv(multlay_out_file, delim_whitespace=True)
    pyemu.gw_utils.apply_hds_obs(multlay_hds_file)
    df2 = pd.read_csv(multlay_out_file, delim_whitespace=True)
    assert len(df1) == len(df2) == np.abs(skipmask).sum(), \
        "array skip failing, expecting {0} obs but returned {1}".format(np.abs(skipmask).sum(), len(df1))
    diff = df1.obsval - df2.obsval
    assert np.allclose(df1.obsval, df2.obsval), abs(diff.max())

    kperk_pairs = [(0, 0), (0, 1), (0, 2), (2, 0), (2, 1), (2, 2)]
    skipmask = m.bas6.ibound.array[0]
    pyemu.gw_utils.setup_hds_obs(multlay_hds_file, kperk_pairs=kperk_pairs,
                                 skip=skipmask)
    df1 = pd.read_csv(multlay_out_file, delim_whitespace=True)
    pyemu.gw_utils.apply_hds_obs(multlay_hds_file)
    df2 = pd.read_csv(multlay_out_file, delim_whitespace=True)
    assert len(df1) == len(df2) == 2 * m.nlay * np.abs(skipmask).sum(), "array skip failing"
    diff = df1.obsval - df2.obsval
    assert np.allclose(df1.obsval, df2.obsval), abs(diff.max())

    kperk_pairs = [(0, 0), (0, 1), (0, 2), (2, 0), (2, 1), (2, 2)]
    skipmask = m.bas6.ibound.array
    pyemu.gw_utils.setup_hds_obs(multlay_hds_file, kperk_pairs=kperk_pairs,
                                 skip=skipmask)
    df1 = pd.read_csv(multlay_out_file, delim_whitespace=True)
    pyemu.gw_utils.apply_hds_obs(multlay_hds_file)
    df2 = pd.read_csv(multlay_out_file, delim_whitespace=True)
    assert len(df1) == len(df2) == 2 * np.abs(skipmask).sum(), "array skip failing"
    diff = df1.obsval - df2.obsval
    assert np.allclose(df1.obsval, df2.obsval), abs(diff.max())


def postprocess_inactive_conc_test():
    import os
    import shutil
    import numpy as np
    import pandas as pd
    try:
        import flopy
    except:
        return
    import pyemu
    bd = os.getcwd()
    model_ws = os.path.join("..", "examples", "Freyberg_transient")

    org_hds_file = os.path.join("utils", "MT3D001.UCN")
    hds_file = os.path.join("temp", "MT3D001.UCN")
    shutil.copy2(org_hds_file, hds_file)
    kij_dict = {"test1": [0, 0, 0], "test2": (1, 1, 1), "inact": [0, 81, 35]}

    m = flopy.modflow.Modflow.load("freyberg.nam", model_ws=model_ws, load_only=[], check=False)
    frun_line, df = pyemu.gw_utils.setup_hds_timeseries(hds_file, kij_dict, model=m, include_path=True, prefix="hds",
                                                        postprocess_inact=1E30)
    os.chdir("temp")
    df0 = pd.read_csv("{0}_timeseries.processed".format(os.path.split(hds_file)[-1]), delim_whitespace=True)
    df1 = pd.read_csv("{0}_timeseries.post_processed".format(os.path.split(hds_file)[-1]), delim_whitespace=True)
    eval(frun_line)
    df2 = pd.read_csv("{0}_timeseries.processed".format(os.path.split(hds_file)[-1]), delim_whitespace=True)
    df3 = pd.read_csv("{0}_timeseries.post_processed".format(os.path.split(hds_file)[-1]), delim_whitespace=True)
    assert np.allclose(df0, df2)
    assert np.allclose(df2.test1, df3.test1)
    assert np.allclose(df2.test2, df3.test2)
    assert np.allclose(df3, df1)
    os.chdir(bd)

def par_knowledge_test():
    import os
    import numpy as np
    import pyemu
    pst_file = os.path.join("pst","pest.pst")
    pst = pyemu.Pst(pst_file)

    tpl_file = os.path.join("utils","pp_locs.tpl")
    str_file = os.path.join("utils","structure.dat")
    pp_df = pyemu.pp_utils.pp_tpl_to_dataframe(tpl_file)
    pkd = {"kr01c01":0.1}
    try:
        cov = pyemu.helpers.geostatistical_prior_builder(pst_file,{str_file:tpl_file},
                                                         par_knowledge_dict=pkd)
    except:
        return
    else:
        raise Exception("should have failed")
    d1 = np.diag(cov.x)


    df = pyemu.gw_utils.pp_tpl_to_dataframe(tpl_file)
    df.loc[:,"zone"] = np.arange(df.shape[0])
    gs = pyemu.geostats.read_struct_file(str_file)
    cov = pyemu.helpers.geostatistical_prior_builder(pst_file,{gs:df},
                                               sigma_range=4)
    nnz = np.count_nonzero(cov.x)
    assert nnz == pst.npar
    d2 = np.diag(cov.x)
    assert np.array_equiv(d1, d2)


def gw_sft_ins_test():
    import os
    import pyemu

    sft_outfile = os.path.join("utils","test_sft.out")
    #pyemu.gw_utils.setup_sft_obs(sft_outfile)
    #pyemu.gw_utils.setup_sft_obs(sft_outfile,start_datetime="1-1-1970")
    pyemu.gw_utils.setup_sft_obs(sft_outfile, start_datetime="1-1-1970",times=[10950.00])


def sfr_helper_test():
    import os
    import shutil
    import pandas as pd
    import pyemu
    import flopy

    #setup the process
    df_sfr = pyemu.gw_utils.setup_sfr_seg_parameters("supply2.nam",model_ws="utils")
    print(df_sfr)
    os.chdir("utils")

    # change the name of the sfr file that will be created
    pars = {}
    with open("sfr_seg_pars.config") as f:
        for line in f:
            line = line.strip().split()
            pars[line[0]] = line[1]
    pars["sfr_filename"] = "test.sfr"
    with open("sfr_seg_pars.config", 'w') as f:
        for k, v in pars.items():
            f.write("{0} {1}\n".format(k, v))

    # change some hcond1 values
    df = pd.read_csv("sfr_seg_pars.dat", delim_whitespace=False,index_col=0)
    df.loc[:, "hcond1"] = 1.0
    df.to_csv("sfr_seg_pars.dat", sep=',')

    # make sure the hcond1 mult worked...
    sd1 = pyemu.gw_utils.apply_sfr_seg_parameters().segment_data[0]
    m1 = flopy.modflow.Modflow.load("supply2.nam", load_only=["sfr"], check=False)
    sd2 = m1.sfr.segment_data[0]

    sd1 = pd.DataFrame.from_records(sd1)
    sd2 = pd.DataFrame.from_records(sd2)

    # print(sd1.hcond1)
    # print(sd2.hcond2)

    assert sd1.hcond1.sum() == sd2.hcond1.sum()

    # change some hcond1 values
    df = pd.read_csv("sfr_seg_pars.dat",delim_whitespace=False,index_col=0)
    df.loc[:,"hcond1"] = 0.5
    df.to_csv("sfr_seg_pars.dat",sep=',')

    #change the name of the sfr file that will be created
    pars = {}
    with open("sfr_seg_pars.config") as f:
        for line in f:
            line = line.strip().split()
            pars[line[0]] = line[1]
    pars["sfr_filename"] = "test.sfr"
    with open("sfr_seg_pars.config",'w') as f:
        for k,v in pars.items():
            f.write("{0} {1}\n".format(k,v))

    #make sure the hcond1 mult worked...
    sd1 = pyemu.gw_utils.apply_sfr_seg_parameters().segment_data[0]
    m1 = flopy.modflow.Modflow.load("supply2.nam",load_only=["sfr"],check=False)
    sd2 = m1.sfr.segment_data[0]

    sd1 = pd.DataFrame.from_records(sd1)
    sd2 = pd.DataFrame.from_records(sd2)

    #print(sd1.hcond1)
    #print(sd2.hcond2)

    os.chdir("..")

    assert (sd1.hcond1 * 2.0).sum() == sd2.hcond1.sum()


def sfr_obs_test():
    import os
    import pyemu
    import flopy

    sfr_file = os.path.join("utils","freyberg.sfr.out")
    pyemu.gw_utils.setup_sfr_obs(sfr_file)
    pyemu.gw_utils.setup_sfr_obs(sfr_file,seg_group_dict={"obs1":[1,4],"obs2":[16,17,18,19,22,23]})

    m = flopy.modflow.Modflow.load("freyberg.nam",model_ws="utils",load_only=[],check=False)
    pyemu.gw_utils.setup_sfr_obs(sfr_file,model=m)
    pyemu.gw_utils.apply_sfr_obs()
    pyemu.gw_utils.setup_sfr_obs(sfr_file, seg_group_dict={"obs1": [1, 4], "obs2": [16, 17, 18, 19, 22, 23]},model=m)


def sfr_reach_obs_test():
    import os
    import pyemu
    import flopy
    import pandas as pd
    import numpy as np

    sfr_file = os.path.join("utils","freyberg.sfr.out")
    pyemu.gw_utils.setup_sfr_reach_obs(sfr_file, seg_reach=[[1, 2], [4, 1], [2, 2]])
    proc = pd.read_csv("{0}.reach_processed".format(sfr_file), sep=' ')
    assert proc.shape[0] == 3*2  # (nper*nobs)
    pyemu.gw_utils.setup_sfr_reach_obs(sfr_file, seg_reach=np.array([[1, 2], [4, 1], [2, 2]]))
    proc = pd.read_csv("{0}.reach_processed".format(sfr_file), sep=' ')
    assert proc.shape[0] == 3*2  # (nper*nobs)
    pyemu.gw_utils.setup_sfr_reach_obs(sfr_file)
    proc = pd.read_csv("{0}.reach_processed".format(sfr_file), sep=' ')
    assert proc.shape[0] == 3*40  # (nper*nobs)
    pyemu.gw_utils.setup_sfr_reach_obs(sfr_file,seg_reach={"obs1": [1, 2], "obs2": [4, 1]})
    proc = pd.read_csv("{0}.reach_processed".format(sfr_file), sep=' ')
    assert proc.shape[0] == 3*2  # (nper*nobs)
    seg_reach_df = pd.DataFrame.from_dict({"obs1": [1, 2], "obs2": [4, 1]}, columns=['segment', 'reach'], orient='index')
    pyemu.gw_utils.setup_sfr_reach_obs(sfr_file, seg_reach=seg_reach_df)
    proc = pd.read_csv("{0}.reach_processed".format(sfr_file), sep=' ')
    assert proc.shape[0] == 3*2  # (nper*nobs)

    m = flopy.modflow.Modflow.load("freyberg.nam", model_ws="utils", load_only=[], check=False)
    pyemu.gw_utils.setup_sfr_reach_obs(sfr_file, model=m)
    pyemu.gw_utils.apply_sfr_reach_obs()
    proc = pd.read_csv("{0}.reach_processed".format(sfr_file), sep=' ')
    assert proc.shape[0] == 3*40  # (nper*nobs)
    pyemu.gw_utils.setup_sfr_reach_obs(sfr_file, seg_reach={"obs1": [1, 2], "obs2": [4, 1], "blah": [2, 1]}, model=m)
    proc = pd.read_csv("{0}.reach_processed".format(sfr_file), sep=' ')
    assert proc.shape[0] == 3*2  # (nper*nobs)
    pyemu.gw_utils.setup_sfr_reach_obs(sfr_file, model=m, seg_reach=seg_reach_df)
    proc = pd.read_csv("{0}.reach_processed".format(sfr_file), sep=' ')
    assert proc.shape[0] == 3*2  # (nper*nobs)


def gage_obs_test():
    import os
    import pyemu
    import numpy as np

    bd = os.getcwd()
    os.chdir("utils")

    gage_file = "RmSouth_pred_7d.gage1.go"
    gage = pyemu.gw_utils.setup_gage_obs(gage_file, start_datetime='2007-04-11')
    if gage is not None:
        print(gage[1], gage[2])

    times = np.concatenate(([0], np.arange(7., 7. * 404, 7.)))
    gage = pyemu.gw_utils.setup_gage_obs(gage_file, start_datetime='2007-04-11', times=times)
    if gage is not None:
        print(gage[1], gage[2])
    pyemu.gw_utils.apply_gage_obs()

    os.chdir(bd)


def pst_from_parnames_obsnames_test():
    import pyemu
    import os

    parnames  = ['param1','par2','p3']
    obsnames  = ['obervation1','ob2','o6']

    pst = pyemu.helpers.pst_from_parnames_obsnames(parnames, obsnames)

    pst.write('simpletemp.pst')

    newpst = pyemu.Pst('simpletemp.pst')

    assert newpst.nobs == len(obsnames)
    assert newpst.npar == len(parnames)


def write_jactest_test():
    import os
    import pyemu

    pst = pyemu.Pst(os.path.join("pst", "5.pst"))
    print(pst.parameter_data)
    #return
    df = pyemu.helpers.build_jac_test_csv(pst,num_steps=5)
    print(df)


    df = pyemu.helpers.build_jac_test_csv(pst, num_steps=5,par_names=["par1"])
    print(df)

    df = pyemu.helpers.build_jac_test_csv(pst, num_steps=5,forward=False)
    print(df)
    df.to_csv(os.path.join("temp","sweep_in.csv"))
    print(pst.parameter_data)
    pst.write(os.path.join("temp","test.pst"))
    #pyemu.helpers.run("sweep test.pst",cwd="temp")

def plot_id_bar_test():
    import pyemu
    import matplotlib.pyplot as plt
    w_dir = "la"
    ev = pyemu.ErrVar(jco=os.path.join(w_dir, "pest.jcb"))
    id_df = ev.get_identifiability_dataframe(singular_value=15)
    pyemu.plot_utils.plot_id_bar(id_df)
    #plt.show()


def jco_from_pestpp_runstorage_test():
    import os
    import pyemu

    jco_file = os.path.join("utils","pest.jcb")
    jco = pyemu.Jco.from_binary(jco_file)

    rnj_file = jco_file.replace(".jcb",".rnj")
    pst_file = jco_file.replace(".jcb",".pst")
    jco2 = pyemu.helpers.jco_from_pestpp_runstorage(rnj_file,pst_file)
    diff = (jco - jco2).to_dataframe()
    print(diff)


def hfb_test():
    import os
    try:
        import flopy
    except:
        return
    import pyemu

    org_model_ws = os.path.join("..", "examples", "freyberg_sfr_update")
    nam_file = "freyberg.nam"
    m = flopy.modflow.Modflow.load(nam_file, model_ws=org_model_ws, check=False)
    try:
        pyemu.gw_utils.write_hfb_template(m)
    except:
        pass
    else:
        raise Exception()

    hfb_data = []
    jcol1, jcol2 = 14,15
    for i in range(m.nrow):
        hfb_data.append([0,i,jcol1,i,jcol2,0.001])
    flopy.modflow.ModflowHfb(m,0,0,len(hfb_data),hfb_data=hfb_data)
    m.change_model_ws("temp")
    m.write_input()
    m.exe_name = "mfnwt"
    try:
        m.run_model()
    except:
        pass

    tpl_file,df = pyemu.gw_utils.write_hfb_template(m)
    assert os.path.exists(tpl_file)
    assert df.shape[0] == m.hfb6.hfb_data.shape[0]


def read_runstor_test():
    import os
    import numpy as np
    import pandas as pd
    import pyemu
    d = os.path.join("utils","runstor")
    pst = pyemu.Pst(os.path.join(d,"pest.pst"))

    par_df,obs_df = pyemu.helpers.read_pestpp_runstorage(os.path.join(d,"pest.rns"),"all")
    par_df2 = pd.read_csv(os.path.join(d,"sweep_in.csv"),index_col=0)
    obs_df2 = pd.read_csv(os.path.join(d,"sweep_out.csv"),index_col=0)
    obs_df2.columns = obs_df2.columns.str.lower()
    obs_df2 = obs_df2.loc[:,obs_df.columns]
    par_df2 = par_df2.loc[:,par_df.columns]
    pdif = np.abs(par_df.values - par_df2.values).max()
    odif = np.abs(obs_df.values - obs_df2.values).max()
    print(pdif,odif)
    assert pdif < 1.0e-6,pdif
    assert odif < 1.0e-6,odif
   
    try:
        pyemu.helpers.read_pestpp_runstorage(os.path.join(d, "pest.rns"), "junk")
    except:
        pass
    else:
        raise Exception()



def smp_test():
    import os
    from pyemu.utils import smp_to_dataframe, dataframe_to_smp, \
        smp_to_ins
    from pyemu.pst.pst_utils import parse_ins_file

    smp_filename = os.path.join("misc", "gainloss.smp")
    df = smp_to_dataframe(smp_filename)
    print(df.dtypes)
    dataframe_to_smp(df, smp_filename + ".test")
    smp_to_ins(smp_filename)
    obs_names = parse_ins_file(smp_filename + ".ins")
    print(len(obs_names))

    smp_filename = os.path.join("misc", "sim_hds_v6.smp")
    df = smp_to_dataframe(smp_filename)
    print(df.dtypes)
    dataframe_to_smp(df, smp_filename + ".test")
    smp_to_ins(smp_filename)
    obs_names = parse_ins_file(smp_filename + ".ins")
    print(len(obs_names))


def smp_dateparser_test():
    import os
    import pyemu
    from pyemu.utils import smp_to_dataframe, dataframe_to_smp, \
        smp_to_ins



    smp_filename = os.path.join("misc", "gainloss.smp")
    df = smp_to_dataframe(smp_filename, datetime_format="%d/%m/%Y %H:%M:%S")
    print(df.dtypes)
    dataframe_to_smp(df, smp_filename + ".test")
    smp_to_ins(smp_filename)
    obs_names = pyemu.pst_utils.parse_ins_file(smp_filename + ".ins")
    print(len(obs_names))

    smp_filename = os.path.join("misc", "sim_hds_v6.smp")
    df = smp_to_dataframe(smp_filename)
    print(df.dtypes)
    dataframe_to_smp(df, smp_filename + ".test")
    smp_to_ins(smp_filename)
    obs_names = pyemu.pst_utils.parse_ins_file(smp_filename + ".ins")
    print(len(obs_names))



def fieldgen_dev():
    import shutil
    import numpy as np
    import pandas as pd
    try:
        import flopy
    except:
        return
    import pyemu
    org_model_ws = os.path.join("..", "examples", "freyberg_sfr_update")
    nam_file = "freyberg.nam"
    m = flopy.modflow.Modflow.load(nam_file, model_ws=org_model_ws, check=False)
    flopy.modflow.ModflowRiv(m, stress_period_data={0: [[0, 0, 0, 30.0, 1.0, 25.0],
                                                        [0, 0, 1, 31.0, 1.0, 25.0],
                                                        [0, 0, 1, 31.0, 1.0, 25.0]]})
    org_model_ws = "temp"
    m.change_model_ws(org_model_ws)
    m.write_input()

    new_model_ws = "temp_fieldgen"

    ph = pyemu.helpers.PstFromFlopyModel(nam_file, new_model_ws=new_model_ws,
                                         org_model_ws=org_model_ws,
                                         grid_props=[["upw.hk", 0], ["rch.rech", 0]],
                                         remove_existing=True,build_prior=False)
    v = pyemu.geostats.ExpVario(1.0,1000,anisotropy=10,bearing=45)
    gs = pyemu.geostats.GeoStruct(nugget=0.0,variograms=v,name="aniso")
    struct_dict = {gs:["hk","ss"]}
    df = pyemu.helpers.run_fieldgen(m,10,struct_dict,cwd=new_model_ws)

    import matplotlib.pyplot as plt
    i = df.index.map(lambda x: int(x.split('_')[0]))
    j = df.index.map(lambda x: int(x.split('_')[1]))
    arr = np.zeros((m.nrow,m.ncol))
    arr[i,j] = df.iloc[:,0]
    plt.imshow(arr)
    plt.show()


if __name__ == "__main__":
    # fieldgen_dev()
    smp_test()
    # smp_dateparser_test()
    # smp_to_ins_test()
    #read_runstor_test()
    #long_names()
    #master_and_slaves()
    #plot_id_bar_test()
    #pst_from_parnames_obsnames_test()
    #write_jactest_test()
    # sfr_obs_test()
    #sfr_reach_obs_test()
    #gage_obs_test()
    #setup_pp_test()
    #sfr_helper_test()
    # gw_sft_ins_test()
    # par_knowledge_test()
    # grid_obs_test()
    # hds_timeseries_test()
    # postprocess_inactive_conc_test()
    # plot_summary_test()
    # load_sgems_expvar_test()
    # read_hydmod_test()
    # make_hydmod_insfile_test()
    # gslib_2_dataframe_test()
    # sgems_to_geostruct_test()
    # #linearuniversal_krige_test()
    # geostat_prior_builder_test()
    # geostat_draws_test()
    #jco_from_pestpp_runstorage_test()
    # mflist_budget_test()
    # mtlist_budget_test()
    # tpl_to_dataframe_test()
    # kl_test()
    # hfb_test()
    #more_kl_test()
    #zero_order_regul_test()
    # first_order_pearson_regul_test()
    # master_and_slaves()
    # smp_to_ins_test()
    # read_pestpp_runstorage_file_test()
    # write_tpl_test()
    # pp_to_shapefile_test()
    # read_pval_test()
    # read_hob_test()
    #setup_pp_test()
    # pp_to_tpl_test()
    # setup_ppcov_complex()
    # ppcov_complex_test()
    # setup_ppcov_simple()
    #ppcov_simple_sparse_test()
    #ppcov_complex_sparse_test()
    #fac2real_test()
    # vario_test()
    # geostruct_test()
    # aniso_test()
    # struct_file_test()
    # covariance_matrix_test()
    # add_pi_obj_func_test()
    # ok_test()
    # ok_grid_test()
    # ok_grid_zone_test()
    # ppk2fac_verf_test()
