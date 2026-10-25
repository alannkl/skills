package cmd

import "github.com/spf13/cobra"

var rootCmd = &cobra.Command{Use: "tally", Short: "Shared expense ledger"}

func Execute() error { return rootCmd.Execute() }
