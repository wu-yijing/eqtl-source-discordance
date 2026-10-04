# 在隔离库里从源码编译安装 MatchIt 4.5.5（renv.lock 钉的版本）
lib <- "E:/workbuddy/_s4_repro/rlib452"
dir.create(lib, showWarnings = FALSE, recursive = TRUE)
.libPaths(c(lib, .libPaths()))
options(repos = c(CRAN = "https://cloud.r-project.org"))

cat("=== 目标库 ===\n"); print(.libPaths())
cat("=== 编译工具 ===\n")
cat("Rtools:", pkgbuild::has_build_tools(debug = FALSE), "\n\n")

install.packages("E:/workbuddy/_s4_repro/src/MatchIt_4.5.5.tar.gz",
                 repos = NULL, type = "source", lib = lib,
                 INSTALL_opts = "--no-multiarch")

cat("\n=== 结果 ===\n")
p <- tryCatch(as.character(packageVersion("MatchIt", lib.loc = lib)),
              error = function(e) NA_character_)
if (is.na(p)) {
  cat("INSTALL FAILED\n")
} else {
  cat("INSTALLED MatchIt", p, "\n")
  ## 确认加载的是隔离库里的那一份，而不是 win-library 的 4.7.2
  suppressMessages(library(MatchIt))
  cat("loaded from:", dirname(dirname(getNamespaceInfo("MatchIt", "path"))), "\n")
  cat("loaded version:", as.character(packageVersion("MatchIt")), "\n")
}
