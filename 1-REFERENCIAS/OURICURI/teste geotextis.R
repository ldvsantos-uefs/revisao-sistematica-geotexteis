library(readxl)
install.packages("psych")
install.packages('knitr')
library(nortest)

library(corrplot)

library(psych)
#comandos externos predefinidos para o Rstudio
library(Rcmdr)
library(ggplot2)
library(PMCMR)

DADOS_TABELADOS <- read_excel("C:/Users/Catuxe/Google Drive/ACADE^MICO/MESTRADO/ARTIGOS/ARTIGO TONY/DADOS_TABELADOS.xlsx")

View(DADOS_TABELADOS)


DADOS_TABELADOS


dados<-(DADOS_TABELADOS)



shapiro.test(dados)



kruskal.test(dados$TRAÇÃO~factor(dados$TRATAMENTO))

posthoc.kruskal.nemenyi.test(dados$TRAÇÃO ~ factor(dados$TRATAMENTO))


krus <- kruskal(dados$TRAÇÃO, dados$TRATAMENTO, alpha = 0.05, p.adj=c("none","holm","hommel",
                                                                          "hochberg", "bonferroni", "BH", "BY", "fdr"), group=TRUE, main = "TESTE DE TRAÇÃO",console=FALSE)
krus





p1 <- model + geom_smooth(method=lm) # Acrescenta a linha de tendência e o intervalo de confiança de predição

plot(TENSÃO~TRATAMENTO)
p1

abline(model)

set.seed(1)
x <-c(0,60,90,120,180)
y <-c(107.56, 40.06, 31.54,56.70, 55.58)



dados <- data.frame(a = sample(y), b = sample(x))
a <- barplot(dados$a, ylim = c(0,130))


points(a, dados$b, ylim= c(0,100))
lines(a, dados$b, ylim= c(0,100))
axis(1, at = a, labels = 2000:2004)








