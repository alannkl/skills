package cmd

import (
	"github.com/spf13/cobra"

	"github.com/tallyhq/tally/internal/syncer"
)

var verbose bool

var syncCmd = &cobra.Command{
	Use:   "sync",
	Short: "Pull the latest ledger from the server",
	RunE: func(cmd *cobra.Command, args []string) error {
		return syncer.Run(cmd.Context(), syncer.Options{Verbose: verbose})
	},
}

func init() {
	syncCmd.Flags().BoolVarP(&verbose, "verbose", "v", false, "print every HTTP request and response")
	rootCmd.AddCommand(syncCmd)
}
