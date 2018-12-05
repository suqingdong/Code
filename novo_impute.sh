chrom_list="21 22"
panel_list="1000G chb_chs"

do_one_phased="Y"
do_two_phased="Y"

input_dir="/NJPROJ2/DISEASE/Research/IMPUTE/data/benchmark/"  # 待填补数据路径
input_pat="benchmark_masked"                                  # 待填补数据文件前缀

nf_dir="/NJPROJ2/DISEASE/Research/IMPUTE/scripts"
data_dir="/NJPROJ2/DISEASE/Research/IMPUTE/data/"
novodb_dir="/NJPROJ2/DISEASE/Research/NovoDB/V10/impute"

addchr=0                    # input_vcf中如含chr则此设为1
phase_thread=8              # shapeit分型线程数
impute2_thread=4            # impute2填补线程数
impute2_chunksize=5000000   # impute2填补区间大小

mkdir -p config shell
rm -f config.txt

for chrom in $chrom_list;do

    if [ ${do_two_phased} == "Y" ];then
# =========================== phase with 1KG ===============================
        echo -e "
params {

    data_dir = \"${data_dir}\"

    work_dir = \"`pwd`\" 

    output_dir = \"\${params.work_dir}/result/phase/\"
    
    input_vcf = \"${novodb_dir}/V10_WGS_all_v2_chr${chrom}_variant.missing01.nomulti.vcf.gz\"
    input_vcf_idx = \"${novodb_dir}/V10_WGS_all_v2_chr${chrom}_variant.missing01.nomulti.vcf.gz.tbi\"

    ref_map_dir = \"\${params.data_dir}/genetic_map/\"
    ref_map_pattern = \"genetic_map_chr%s_combined_b37.txt\"

    ref_panel_dir = \"\${params.data_dir}/1000G/\"
    ref_hap_pattern = \"1000GP_Phase3_chr%s.hap.gz\"
    ref_leg_pattern = \"1000GP_Phase3_chr%s.legend.gz\"
    ref_sample = \"1000GP_Phase3.sample\"

    chromosomes_List = [${chrom}]

    addchr = ${addchr}

    phase_thread = ${phase_thread}
}

timeline {
    enabled=true
    file = \"\${params.output_dir}/log/chr${chrom}.phase_timeline.html\"
}

report {
    enabled = true
    file = \"\${params.output_dir}/log/chr${chrom}.phase_report.html\"
}
" > config/chr${chrom}.phase.config
# ========================================

        echo -e "
    set -eo pipefail

    cd $(pwd)

    echo step1: phase ${chrom} start: \$(date)

    nextflow run \\
        ${nf_dir}/phase.nf \\
        -c config/chr${chrom}.phase.config

    echo step1: phase ${chrom} done: \$(date)
    " > shell/chr${chrom}.step1.phase.sh

        echo shell/chr${chrom}.step1.phase.sh 50G ${phase_thread} >> config.txt

    fi
# =========================== phase with 1KG done ===============================


    for panel in ${panel_list};do

        if [ $panel == '1000G' ];then
            ref_hap_pattern='1000GP_Phase3_chr%s.hap.gz'
            ref_leg_pattern='1000GP_Phase3_chr%s.legend.gz'
        else
            ref_hap_pattern='chinese-han.chr%s.phase3.genotypes.hap.gz'
            ref_leg_pattern='chinese-han.chr%s.phase3.genotypes.legend.gz'
        fi

        if [ ${do_two_phased} == "Y" ];then
# =========================== two phased impute ===============================
            echo -e "
params {

    data_dir = \"${data_dir}\"

    work_dir = \"$(pwd)\"

    output_dir = \"\${params.work_dir}/result/${panel}_two_phased\"

    input_dir = \"${input_dir}\"
    input_pat = \"${input_pat}\"
    
    chromosomes_List = [${chrom}]
    chromosomeSizesFile = \"\${params.data_dir}/hg19_chromosomes_size/hg19_chromosomes_size.txt\"

    map_dir = \"\${params.data_dir}/genetic_map/\"
    map_pattern = \"genetic_map_chr%s_combined_b37.txt\"

    ref_panel_dir = \"\${params.data_dir}/${panel}/\"
    ref_hap_pattern = \"${ref_hap_pattern}\"
    ref_leg_pattern = \"${ref_leg_pattern}\"

    custom_panel_dir = \"\${params.work_dir}/result/phase/\"
    custom_hap_pattern = \"chr%s_phased.hap\"
    custom_leg_pattern = \"chr%s_phased.leg\"

    addchr = ${addchr}

    plink_thread = 4
    plink_memory = 512

    impute2_thread = ${impute2_thread}
    impute2_chunksize = ${impute2_chunksize}
}

timeline {
    enabled=true
    file = \"\${params.output_dir}/log/chr${chrom}.${panel}.impute_two_phased.timeline.html\"
}

report {
    enabled = true
    file = \"\${params.output_dir}/log/chr${chrom}.${panel}.impute_two_phased.report.html\"
}
" > config/chr${chrom}.${panel}.impute_two_phased.config
# ===================================================


            echo -e "
set -e
echo step2: impute two phased for ${chrom} - ${panel} start: `date`

cd $(pwd)

nextflow run \\
    ${nf_dir}/impute_with_twophased.nf \\
    -c config/chr${chrom}.${panel}.impute_two_phased.config

echo step2: impute two phased for ${chrom} - ${panel} done: `date`
" > shell/chr${chrom}.${panel}.step2.impute_two_phased.sh

            echo shell/chr${chrom}.${panel}.step2.impute_two_phased.sh 90G shell/chr${chrom}.step1.phase.sh 4 >> config.txt
        fi
# ======================= two phased impute done ============================



# =========================== one phased impute ===============================
        if [ ${do_one_phased} == "Y" ];then
            echo -e "
    
params {

    data_dir = \"${data_dir}\"

    work_dir = \"$(pwd)\"

    output_dir = \"\${params.work_dir}/result/${panel}_one_phased/\"

    input_dir = \"${input_dir}\"
    input_pat = \"${input_pat}\"
    
    chromosomes_List = [${chrom}]
    chromosomeSizesFile = \"\${params.data_dir}/hg19_chromosomes_size/hg19_chromosomes_size.txt\"

    input_vcf = \"${novodb_dir}/V10_WGS_all_v2_chr${chrom}_variant.missing01.nomulti.vcf.gz\"

    map_dir = \"\${params.data_dir}/genetic_map/\"
    map_pattern = \"genetic_map_chr%s_combined_b37.txt\"

    ref_panel_dir = \"\${params.data_dir}/${panel}/\"
    ref_hap_pattern = \"${ref_hap_pattern}\"
    ref_leg_pattern = \"${ref_leg_pattern}\"

    addchr = ${addchr}

    plink_thread = 4
    plink_memory = 512

    impute2_thread = ${impute2_thread}
    impute2_chunksize = ${impute2_chunksize}
}

timeline {
    enabled=true
    file = \"\${params.output_dir}/log/chr${chrom}.${panel}.impute_one_phased.timeline.html\"
}

report {
    enabled = true
    file = \"\${params.output_dir}/log/chr${chrom}.${panel}.impute_one_phased.report.html\"
}


" > config/chr${chrom}.${panel}.impute_one_phased.config


            echo -e "
set -e
echo step3: impute one phased for ${chrom} - ${panel} start: `date`

cd $(pwd)

nextflow run \\
    ${nf_dir}/impute_with_onephased_oneunphased.nf \\
    -c config/chr${chrom}.${panel}.impute_one_phased.config

echo step3: impute one phased for ${chrom} - ${panel} done: `date`
" > shell/chr${chrom}.${panel}.step3.impute_one_phased.sh

    
            echo shell/chr${chrom}.${panel}.step3.impute_one_phased.sh 90G 4 >> config.txt

        fi
# =========================== one phased impute done ===============================

    done
done

chmod 755 shell/*sh
