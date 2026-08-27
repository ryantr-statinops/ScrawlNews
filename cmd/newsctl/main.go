package main

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "newsctl",
	Short: "ScrawlNews control CLI (stub, Go-base infra)",
	Long:  "Stub CLI for ScrawlNews local dashboard. Pipeline logic stays in Python (FastAPI+Celery).",
}

var runCmd = &cobra.Command{
	Use:   "run",
	Short: "Trigger pipeline run via API",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("newsctl run: stub — calls POST http://localhost/api/runs (Python FastAPI)")
		fmt.Println("TODO: implement HTTP client to trigger Celery pipeline_run")
	},
}

var historyCmd = &cobra.Command{
	Use:   "history",
	Short: "Show pipeline runs",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("newsctl history: stub — calls GET http://localhost/api/runs")
	},
}

func init() {
	rootCmd.AddCommand(runCmd)
	rootCmd.AddCommand(historyCmd)
}

func main() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
