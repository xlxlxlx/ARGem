library(dplyr)
library(vegan)

#Set working directory
setwd("~/Desktop/Problem_Solving/Data_analysis/Analysis/NMDS/NMDS_plots")

#Read the transposed file for the genes normalized by the method you choose, here TPM is chosen.
file.spp<- read.csv("~/Desktop/Problem_Solving/Data_analysis/Analysis/NMDS/NMDS_plot_sheets/16S_full_gene_trans.csv", header = TRUE, sep = ',') %>% tbl_df()
file.spp <- file.spp[ -c(1) ]

#Read file that identifies and categorizes the Samples ie. Season, Year, etc.
file.spp_groups <- read.csv("~/Desktop/Problem_Solving/Data_analysis/Analysis/NMDS/NMDS_plot_sheets/group_data.csv", header = TRUE, sep = ',') %>% tbl_df()

##Calculate distance for clustering
file.spp_distmat <- vegdist(file.spp, method = 'bray', na.rm = TRUE)
file.spp_dismat <- as.matrix(file.spp_distmat, labels = T)
#write.csv(file.spp_dismat, "../NMDS_plot_sheets/vegan_distance/file_dist_16S_final.csv")

##Extract order from dendogram 
hclust <- hclust(file.spp_distmat)
plot(hclust)

#Define clustering cut off
hclust_ct<- as.matrix(cutree(hclust , 3))
write.csv(hclust_ct, "../NMDS_plot_sheets/hclust/16S_hclust_ct3.csv")

#Add clustering as parameter to group datafile
hc <- read.csv("../NMDS_plot_sheets/hclust/16S_hclust_ct3.csv", sep = ',', header = TRUE) %>% tbl_df()
file.spp_groups$order = hc$V1
write.csv(file.spp_groups, "../NMDS_plot_sheets/16S_hclust_info.csv")

#Run anosim
ano_Season = anosim(file.spp_dismat, file.spp_groups$Paper, distance = "bray", permutations = 9999)
ano_Season

ano_Cluster = anosim(file.spp_dismat, file.spp_groups$Paper, distance = "bray", permutations = 9999)
ano_Cluster

ano_Paper = anosim(file.spp_dismat, file.spp_groups$Paper, distance = "bray", permutations = 9999)
ano_Paper

##Run metaMDS for NDMS2 plotting
file.spp_NMS <-
  metaMDS(file.spp_distmat,
          distance = "bray",
          k = 3,
          maxit = 999, 
          trymax = 500,
          wascores = TRUE)

##Plot and save as pdf
pdf('variations/NMDS_16S_coloryear.pdf')
colvec <- rainbow(9)  # Identifies colors for group assignments
pchvec <- 1:2   ## Identifies shapes for group assignments

plot(file.spp_NMS, main = 'NMDS Plot with 16S Normalization', col = colvec)
with(file.spp_groups,
     points(file.spp_NMS,
            display = "sites",
            col = colvec[Year],
            pch = pchvec[Season]
     ))

ordiellipse(file.spp_NMS, file.spp_groups$order, display = "sites", conf = 0.90)

with(file.spp_groups, legend(x="bottomleft", legend=levels(factor(Year)), col= colvec, pch = 1, bty = "n", horiz=TRUE, title="Year", x.intersp = .4, y.intersp = .7))
with(file.spp_groups, legend(x="bottomright", legend=levels(Season), pch = unique(Season), bty = "n", title="Season", horiz=TRUE, x.intersp = .4, y.intersp = .7))

dev.off()
