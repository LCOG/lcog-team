// //////////////////////////
// WATCH THOSE MONTH CODES //
/////////////////////////////

export const releases = [
  {
    version: '1.1.0',
    date: new Date(2025, 11, 22),
    changes: [
      {
        type: 'new',
        description: 'New Phishing management app.'
      },
      {
        type: 'improved',
        description: 'Minor improvements to Performance Review app.'
      }
    ]
  },
  {
    version: '1.0.0',
    date: new Date(2025, 11, 4),
    changes: [
      {
        type: 'new',
        description: 'Deployment on ECS so it\'s time for v1.'
      },
      {
        type: 'improved',
        description: 'Minor improvements to Performance Review and CC modules.'
      }
    ]
  },
  {
    version: '0.52.0',
    date: new Date(2025, 9, 7),
    changes: [
      {
        type: 'improved',
        description: 'Updated employee transition form.'
      },
      {
        type: 'improved',
        description: 'Security updates to API endpoints.'
      },
      {
        type: 'improved',
        description: 'Minor updates to PRs.'
      },
      {
        type: 'fix',
        description: 'Fix to PR dashboard that caused a page crash.'
      },
    ]
  },
  {
    version: '0.51.0',
    date: new Date(2025, 8, 1),
    changes: [
      {
        type: 'improved',
        description: 'Update Django 4.2 -> 5.2.'
      },
      {
        type: 'improved',
        description: 'Updates to security messages.'
      },
      {
        type: 'improved',
        description: 'Send weekly reminders for workflow steps.'
      },
    ]
  },
  {
    version: '0.50.0',
    date: new Date(2025, 6, 21),
    changes: [
      {
        type: 'improved',
        description: 'Many improvements to Performance Reviews module.'
      },
    ]
  },
  {
    version: '0.49.2',
    date: new Date(2025, 5, 24),
    changes: [
      {
        type: 'improved',
        description: 'Major overhaul of Performance Reviews module. Update ' +
          'the dashboard to match the more modern Workflows layout. Refactor ' +
          'to use the modern Pinia store.'
      },
    ]
  },
  {
    version: '0.49.1',
    date: new Date(2025, 4, 20),
    changes: [
      {
        type: 'fix',
        description: 'Minor bugfixes'
      },
    ]
  },
  {
    version: '0.49.0',
    date: new Date(2025, 4, 13),
    changes: [
      {
        type: 'new',
        description: 'Organizations model for multi-tenant instances.'
      },
      {
        type: 'improved',
        description: 'CC: Don\'t allow selecting the same card twice in the ' +
          'same month.'
      },
      {
        type: 'improved',
        description: 'API security improvements.'
      },
    ]
  },
  {
    version: '0.48.0',
    date: new Date(2025, 3, 30),
    changes: [
      {
        type: 'new',
        description: 'PR: Customizable performance review forms.'
      },
      {
        type: 'new',
        description: 'WF: New name change transition and form.'
      },
      {
        type: 'improved',
        description: 'CC: Clean up purchase amounts with commas and negatives.'
      },
    ]
  },
  {
    version: '0.47.0',
    date: new Date(2025, 3, 10),
    changes: [
      {
        type: 'improved',
        description: 'Optimization of how CC expense months and statements ' +
          'are loaded.'
      },
      {
        type: 'improved',
        description: 'Add contractors to employee transitions.'
      },
      {
        type: 'improved',
        description: 'Minor improvements to workflows UI.'
      },
      {
        type: 'improved',
        description: 'Improved backend filtering.'
      },
    ]
  },
  {
    version: '0.46.2',
    date: new Date(2025, 2, 5),
    changes: [
      {
        type: 'improved',
        description: 'Minor improvements to the app.'
      },
    ]
  },
  {
    version: '0.46.1',
    date: new Date(2025, 1, 13),
    changes: [
      {
        type: 'improved',
        description: 'Minor improvements to the app.'
      },
    ]
  },
  {
    version: '0.46.0',
    date: new Date(2025, 1, 5),
    changes: [
      {
        type: 'new',
        description: 'Add peer feedback to performance reviews.'
      },
      {
        type: 'improved',
        description: 'Improvements to performance review form.'
      },
      {
        type: 'improved',
        description: 'Minor improvements to the CC app fiscal views.'
      },
    ]
  },
  {
    version: '0.45.4',
    date: new Date(2025, 0, 28),
    changes: [
      {
        type: 'fix',
        description: 'Fix a bug where notifications can get sent to credit ' +
          'card submitters incorrectly.'
      },
      {
        type: 'improved',
        description: 'Improvements to credit card fiscal view.'
      }
    ]
  },
  {
    version: '0.45.2',
    date: new Date(2025, 0, 14),
    changes: [
      {
        type: 'improved',
        description: 'Improve workflow deleted and completed views.'
      },
      {
        type: 'improved',
        description: 'Fiscal can download zip files of ExpenseMonth receipts.'
      }
    ]
  },
  {
    version: '0.45.1',
    date: new Date(2025, 0, 9),
    changes: [
      {
        type: 'improved',
        description: 'Improve Credit Card submitter notifications.'
      },
      {
        type: 'improved',
        description: 'Display Credit Card statement cleared statuses.'
      }
    ]
  },
  {
    version: '0.45.0',
    date: new Date(2025, 0, 7),
    changes: [
      {
        type: 'improved',
        description: 'Various under-the-hood improvements.'
      }
    ]
  },
  {
    version: '0.44.0',
    date: new Date(2024, 11, 27),
    changes: [
      {
        type: 'new',
        description: 'Hold desks for specific employees on specific dates.'
      }
    ]
  },
  {
    version: '0.43.1',
    date: new Date(2024, 11, 20),
    changes: [
      {
        type: 'improved',
        description: 'Performance improvements to the CC app.'
      },
      {
        type: 'fix',
        description: 'Fix a bug on the employee transition form.'
      }
    ]
  },
  {
    version: '0.43.0',
    date: new Date(2024, 11, 17),
    changes: [
      {
        type: 'new',
        description: 'Add activity field to CC expenses.'
      },
      {
        type: 'improved',
        description: 'Approvers can edit some CC expense fields.'
      },
      {
        type: 'improved',
        description: 'Minor improvements to employee onboarding process.'
      },
      {
        type: 'improved',
        description: 'Minor improvements to the CC expenses app.'
      }
    ]
  },
  {
    version: '0.42.0',
    date: new Date(2024, 11, 4),
    changes: [
      {
        type: 'improved',
        description: 'Update backed libraries.'
      },
      {
        type: 'improved',
        description: 'Backend improvements to the workflows app.'
      },
      {
        type: 'improved',
        description: 'Minor improvements to the CC expenses app.'
      }
    ]
  },
  {
    version: '0.41.2',
    date: new Date(2024, 10, 5),
    changes: [
      {
        type: 'new',
        description: 'Add a workflows app help page.'
      },
      {
        type: 'improved',
        description: 'Backend improvements to the workflows app.'
      }
    ]
  },
  {
    version: '0.41.1',
    date: new Date(2024, 10, 1),
    changes: [
      {
        type: 'improved',
        description: 'Backend improvements to the workflows app.'
      },
      {
        type: 'improved',
        description: 'Backend improvements to the CC expenses app.'
      }
    ]
  },
  {
    version: '0.41.0',
    date: new Date(2024, 9, 30),
    changes: [
      {
        type: 'improved',
        description: 'Backend improvements to the workflows app.'
      }
    ]
  },
  {
    version: '0.40.0',
    date: new Date(2024, 9, 29),
    changes: [
      {
        type: 'improved',
        description: 'Backend improvements to the credit card app.'
      }
    ]
  },
  {
    version: '0.39.0',
    date: new Date(2024, 9, 28),
    changes: [
      {
        type: 'new',
        description: 'Credit card submitters can now submit to multiple cards.'
      }
    ]
  },
  {
    version: '0.38.0',
    date: new Date(2024, 9, 22),
    changes: [
      {
        type: 'improved',
        description: 'Improvements to process completion.'
      },
      {
        type: 'improved',
        description: 'Updates to employee transition forms.'
      }
    ]
  },
  {
    version: '0.37.1',
    date: new Date(2024, 8, 27),
    changes: [
      {
        type: 'improved',
        description: 'Allow negative values for credit card expenses.'
      },
      {
        type: 'improved',
        description: 'Better indicate to directors and fiscal the need to ' +
          'approve expenses.'
      },
      {
        type: 'improved',
        description: 'Minor changes to employee transitions workflows.'
      }
    ]
  },
  {
    version: '0.37.0',
    date: new Date(2024, 8, 23),
    changes: [
      {
        type: 'improved',
        description: 'Indicate when action is required on workflow processes.'
      },
      {
        type: 'improved',
        description: 'Notify responsible parties when action is required on ' +
          'workflow processes. Digest email for managers.'
      },
      {
        type: 'improved',
        description: 'Minor changes to employee transition form.'
      }
    ]
  },
  {
    version: '0.36.0',
    date: new Date(2024, 8, 17),
    changes: [
      {
        type: 'improved',
        description: 'Fiscal can lock expense months.'
      }
    ]
  },
  {
    version: '0.35.1',
    date: new Date(2024, 8, 11),
    changes: [
      {
        type: 'new',
        description: 'Credit card expenses app help documentation.'
      },
      {
        type: 'improved',
        description: 'Behind-the-scenes improvements to the credit card ' +
          'expenses app.'
      }
    ]
  },
  {
    version: '0.35.0',
    date: new Date(2024, 8, 5),
    changes: [
      {
        type: 'new',
        description: 'Interns and temporary employees in onboarding forms.'
      },
      {
        type: 'fix',
        description: 'Minor fixes to CC expenses app.'
      }
    ]
  },
  {
    version: '0.34.0',
    date: new Date(2024, 7, 29),
    changes: [
      {
        type: 'improved',
        description: 'Improvements to the credit card expenses app.'
      },
    ]
  },
  {
    version: '0.33.0',
    date: new Date(2024, 7, 28),
    changes: [
      {
        type: 'new',
        description: 'Expenses can be set to repeat from month to month.'
      },
      {
        type: 'improved',
        description: 'Minor improvements to the credit card expenses app.'
      },
      {
        type: 'fix',
        description: 'Add missing profile links to transition emails.'
      },
    ]
  },
  {
    version: '0.32.0',
    date: new Date(2024, 7, 16),
    changes: [
      {
        type: 'improved',
        description: 'Improvements to the credit card expenses app.'
      },
    ]
  },
  {
    version: '0.31.1',
    date: new Date(2024, 7, 5),
    changes: [
      {
        type: 'improved',
        description: 'Improvements to the credit card expenses app.'
      },
    ]
  },
  {
    version: '0.31.0',
    date: new Date(2024, 6, 24),
    changes: [
      {
        type: 'improved',
        description: 'Added notifications for credit card expenses app.'
      },
      {
        type: 'improved',
        description: 'Added more settings for email opt-out.'
      },
    ]
  },
  {
    version: '0.30.1',
    date: new Date(2024, 6, 18),
    changes: [
      {
        type: 'improved',
        description: 'Minor changes to the credit card reconciliation app.'
      },
    ]
  },
  {
    version: '0.30.0',
    date: new Date(2024, 6, 8),
    changes: [
      {
        type: 'improved',
        description: 'Significant overhaul of credit card reconciliation app.'
      },
      {
        type: 'improved',
        description: 'Check out reserved desks at 6:30 PM.'
      }
    ]
  },
  {
    version: '0.29.0',
    date: new Date(2024, 4, 8),
    changes: [
      {
        type: 'new',
        description: 'Credit card reconciliation app.'
      },
      {
        type: 'improved',
        description: 'Restrict desk reservations to 6AM-5PM.'
      },
      {
        type: 'improved',
        description: 'New desk reservation reports.'
      },
    ]
  },
  {
    version: '0.28.0',
    date: new Date(2024, 4, 8),
    changes: [
      {
        type: 'improved',
        description: 'Improved support for custom workflows.'
      },
      {
        type: 'improved',
        description: 'Improved employee transition UI.'
      },
      {
        type: 'improved',
        description: 'Add "Oregon Access" field for onboarding S&DS employees.'
      }
    ]
  },
  {
    version: '0.27.0',
    date: new Date(2024, 4, 2),
    changes: [
      {
        type: 'new',
        description: 'Support for custom workflows.'
      },
      {
        type: 'new',
        description: 'Add custom workflow dashboard display options to profile.'
      },
      {
        type: 'new',
        description: 'Send an early warning transition email to HR.'
      },
      {
        type: 'improved',
        description: 'Only show TORs for approval to manager that are less ' +
          'than 30 days in the past.'
      },
      {
        type: 'improved',
        description: 'Credit card reconciliation demo features.'
      },
      {
        type: 'improved',
        description: 'Usability and speed improvements to time off app.'
      },
      {
        type: 'improved',
        description: 'Display public note in team time off email notifications.'
      },
      {
        type: 'improved',
        description: 'Updated Schaefers kiosk page.'
      },
      {
        type: 'improved',
        description: 'Allow decimals in cubicle number field in transition ' +
          'forms.'
      },
      {
        type: 'fix',
        description: 'Fixed a bug where all workflows were getting shown to ' +
          'everyone in their profile.'
      }
    ]
  },
  {
    version: '0.26.0',
    date: new Date(2024, 3, 18),
    changes: [
      {
        type: 'improved',
        description: 'Credit card reconciliation demo features.'
      },
      {
        type: 'improved',
        description: 'Updated Schaefers kiosk page.'
      }
    ]
  },
  {
    version: '0.25.0',
    date: new Date(2024, 3, 5),
    changes: [
      {
        type: 'new',
        description: 'Added email logging.'
      },
      {
        type: 'improved',
        description: 'Desk numbers are unique. Holds can be deactivated.'
      },
      {
        type: 'improved',
        description: 'Added tooltips to workflow table buttons.'
      },
      {
        type: 'improved',
        description: 'Security updates.'
      }
    ]
  },
  {
    version: '0.24.1',
    date: new Date(2024, 2, 8),
    changes: [
      {
        type: 'improved',
        description: 'Security updates.'
      }
    ]
  },
  {
    version: '0.24.0',
    date: new Date(2024, 1, 27),
    changes: [
      {
        type: 'improved',
        description: 'Improve backend JobTitle interface.'
      }
    ]
  },
  {
    version: '0.23.1',
    date: new Date(2024, 1, 1),
    changes: [
      {
        type: 'improved',
        description: 'Employee transition workflows cannot be completed until' +
          ' the transition form has been completed.'
      },
      {
        type: 'improved',
        description: 'File uploader now auto-uploads.'
      },
      {
        type: 'improved',
        description: 'Security updates'
      }
    ]
  },
  {
    version: '0.23.0',
    date: new Date(2024, 0, 10),
    changes: [
      {
        type: 'new',
        description: 'Organization list and employee profile views for ' +
          'managers to view their employees\' performance reviews.'
      },
      {
        type: 'new',
        description: 'Employee transition form system change date field.'
      },
      {
        type: 'improved',
        description: 'Sort performance review tables by date of review. Color' +
          ' when late.'
      },
      {
        type: 'improved',
        description: 'Add rich text input to performance review forms.'
      }
    ]
  },
  {
    version: '0.22.0',
    date: new Date(2023, 11, 22),
    changes: [
      {
        type: 'improved',
        description: 'Performance improvements for the Workflows module.'
      }
    ]
  },
  {
    version: '0.21.1',
    date: new Date(2023, 11, 21),
    changes: [
      {
        type: 'improved',
        description: 'Migrate Performance Reviews module to the new Vue 3 app.'
      }
    ]
  },
  {
    version: '0.21.0',
    date: new Date(2023, 11, 1),
    changes: [
      {
        type: 'improved',
        description: 'Improvements to transition form.'
      },
      {
        type: 'improved',
        description: 'Security improvements.'
      }
    ]
  },
  {
    version: '0.20.8',
    date: new Date(2023, 10, 29),
    changes: [
      {
        type: 'improved',
        description: 'Improvements to transition form.'
      }
    ]
  },
  {
    version: '0.20.7',
    date: new Date(2023, 10, 14),
    changes: [
      {
        type: 'improved',
        description: 'Improvements to transition form.'
      }
    ]
  },
  {
    version: '0.20.6',
    date: new Date(2023, 10, 13),
    changes: [
      {
        type: 'improved',
        description: 'Security updates.'
      }
    ]
  },
  {
    version: '0.20.5',
    date: new Date(2023, 10, 6),
    changes: [
      {
        type: 'improved',
        description: 'Credit card reconciliation demo features.'
      }
    ]
  },
  {
    version: '0.20.4',
    date: new Date(2023, 10, 6),
    changes: [
      {
        type: 'improved',
        description: 'Minor change to employee transition form.'
      }
    ]
  },
  {
    version: '0.20.3',
    date: new Date(2023, 9, 21),
    changes: [
      {
        type: 'improved',
        description: 'Minor change to employee transition form.'
      }
    ]
  },
  {
    version: '0.20.2',
    date: new Date(2023, 9, 21),
    changes: [
      {
        type: 'fix',
        description: 'Fix a bug where Gas PIN notifications were not being ' +
          'sent for employee transitions.'
      }
    ]
  },
  {
    version: '0.20.1',
    date: new Date(2023, 9, 18),
    changes: [
      {
        type: 'improved',
        description: 'Various improvements to the employee transition form.'
      },
      {
        type: 'improved',
        description: 'Security updates'
      }
    ]
  },
  {
    version: '0.20.0',
    date: new Date(2023, 9, 13),
    changes: [
      {
        type: 'new',
        description: 'Demo credit card reimbursements pages.'
      },
      { type: 'new',
        description: 'View floor plan map in employee transition form.'
      },
      {
        type: 'fix',
        description: 'Fixes to employee transition form.'
      },
    ]
  },
  {
    version: '0.19.2',
    date: new Date(2023, 9, 9),
    changes: [
      { type: 'new',
        description: 'Add Expenses module to track employee expenses.'
      },
      {
        type: 'improved',
        description: 'Various improvements to workflows.'
      },
      {
        type: 'fix',
        description: 'Fixed some issues with employee transitions.'
      },
    ]
  },
  {
    version: '0.19.1',
    date: new Date(2023, 8, 29),
    changes: [
      {
        type: 'improved',
        description: 'Various updates to the transition form process.'
      },
    ]
  },
  {
    version: '0.19.0',
    date: new Date(2023, 8, 27),
    changes: [
      {
        type: 'improved',
        description: 'Employee transition forms can now be assigned.'
      },
      {
        type: 'improved',
        description: 'Track who has and has not viewed security messages in ' +
          'the admin.'
      },
    ]
  },
  {
    version: '0.18.2',
    date: new Date(2023, 8, 19),
    changes: [
      {
        type: 'improved',
        description: 'Performance updates to workflow views.'
      },
    ]
  },
  {
    version: '0.18.1',
    date: new Date(2023, 8, 15),
    changes: [
      {
        type: 'fix',
        description: 'Fixed an issue that caused some workflow tables to ' +
          'never load.'
      }
    ]
  },
  {
    version: '0.18.0',
    date: new Date(2023, 8, 13),
    changes: [
      {
        type: 'improved',
        description: 'Employee transition forms now have an assignee.'
      },
      {
        type: 'improved',
        description: 'Various updates to the transition form.'
      },
      {
        type: 'improved',
        description: 'Security and reliability improvements.'
      }
    ]
  },
  {
    version: '0.17.2',
    date: new Date(2023, 8, 6),
    changes: [
      {
        type: 'improved',
        description: 'Security and reliability improvements.'
      }
    ]
  },
  {
    version: '0.17.1',
    date: new Date(2023, 7, 25),
    changes: [
      {
        type: 'improved',
        description: 'Various improvements to the transition form.'
      }
    ]
  },
  {
    version: '0.17.0',
    date: new Date(2023, 7, 14),
    changes: [
      {
        type: 'improved',
        description: 'Various improvements to the transition form.'
      }
    ]
  },
  {
    version: '0.16.0',
    date: new Date(2023, 7, 9),
    changes: [
      {
        type: 'improved',
        description: 'Various improvements to the transition form.'
      }
    ]
  },
  {
    version: '0.15.3',
    date: new Date(2023, 7, 7),
    changes: [
      {
        type: 'improved',
        description: 'Add a button for hiring managers to send transition ' +
          'email to SDS hiring admins.'
      }
    ]
  },
  {
    version: '0.15.2',
    date: new Date(2023, 7, 4),
    changes: [
      {
        type: 'improved',
        description: 'Minor improvements to the transition form.'
      }
    ]
  },
  {
    version: '0.15.1',
    date: new Date(2023, 7, 2),
    changes: [
      {
        type: 'improved',
        description: 'Minor improvements to the transition form.'
      },
      {
        type: 'improved',
        description: 'Minor improvements to the responsibilities table.'
      },
      {
        type: 'improved',
        description: 'Minor improvements to time off views.'
      }
    ]
  },
  {
    version: '0.15.0',
    date: new Date(2023, 6, 24),
    changes: [
      {
        type: 'new',
        description: 'Add pre-approved leave without pay to transition form'
      },
      {
        type: 'improved',
        description: 'Start transition workflow processes once a STN email is' +
          ' sent.'
      },
      {
        type: 'improved',
        description: 'Improve API access guards.'
      },
      {
        type: 'improved',
        description: 'Workflows can now be manually marked as complete.'
      },
      {
        type: 'improved',
        description: 'Minor improvements to workflows app.'
      }
    ]
  },
  {
    version: '0.14.0',
    date: new Date(2023, 6, 11),
    changes: [
      {
        type: 'improved',
        description: 'Mark if action is required for the current user to ' +
          'complete a workflow step.'
      },
      {
        type: 'improved',
        description: 'Workflows are now archived rather than deleted. They ' +
          'can be restored from the archive.'
      },
      {
        type: 'improved',
        description: 'We no longer create process instances until the ' +
          'transition form is sent to Staff Transition News.'
      },
      {
        type: 'improved',
        description: 'Minor improvements to workflows app.'
      },
      {
        type: 'fix',
        description: 'Fix the way we calculate workflow percent complete.'
      },
      {
        type: 'fix',
        description: 'Display all job titles in the transition form dropdown.'
      }
    ]
  },
  {
    version: '0.13.7',
    date: new Date(2023, 6, 3),
    changes: [
      {
        type: 'improved',
        description: 'Split out workflows by type in dashboard: onboarding, ' +
          'returning, changing, exiting.'
      }
    ]
  },
  {
    version: '0.13.6',
    date: new Date(2023, 5, 29),
    changes: [
      {
        type: 'improved',
        description: 'Many improvements to transition form.'
      },
      {
        type: 'improved',
        description: 'Send notification about Gas PIN for new employees.'
      }
    ]
  },
  {
    version: '0.13.5',
    date: new Date(2023, 5, 27),
    changes: [
      {
        type: 'improved',
        description: 'Added a second language select dropdown to transition ' +
          'form.'
      },
      {
        type: 'improved',
        description: 'Show percent complete in process instance views.'
      },
      {
        type: 'fix',
        description: 'Fix a bug where the transition form would not submit ' +
          'initially.'
      }
    ]
  },
  {
    version: '0.13.4',
    date: new Date(2023, 5, 21),
    changes: [
      {
        type: 'improved',
        description: 'Optimize workflow dashboards.'
      }
    ]
  },
  {
    version: '0.13.3',
    date: new Date(2023, 5, 20),
    changes: [
      {
        type: 'improved',
        description: 'Improvements to employee transition form.'
      }
    ]
  },
  {
    version: '0.13.2',
    date: new Date(2023, 5, 9),
    changes: [
      {
        type: 'new',
        description: 'Workflows archive page'
      },
      {
        type: 'new',
        description: 'Transition form print view'
      },
      {
        type: 'new',
        description: 'Transition form function to send form to staff ' +
          'transition news'
      },
      {
        type: 'improved',
        description: 'Add security for view and edit of transition form fields'
      },
      {
        type: 'improved',
        description: 'Various improvements to workflows pages'
      }
    ]
  },
  {
    version: '0.13.1',
    date: new Date(2023, 4, 30),
    changes: [
      {
        type: 'new',
        description: 'Allow undoing a workflow step'
      },
      {
        type: 'new',
        description: 'Keep change records for the transition form'
      },
      {
        type: 'improved',
        description: 'Various improvements to workflows pages'
      },
      {
        type: 'improved',
        description: 'When showing responsibility conflicts in the calendar, ' +
          'show all conflicts, not just the first one'
      },
    ]
  },
  {
    version: '0.13.0',
    date: new Date(2023, 4, 23),
    changes: [
      {
        type: 'fix',
        description: 'Fix a bug where employee transition form could not be ' +
          'submitted'
      },
      {
        type: 'improved',
        description: 'Employee transition form improvements, including new ' +
          'cell phone fields'
      },
      {
        type: 'improved',
        description: 'Loading spinners in more places'
      },
    ]
  },
  {
    version: '0.12.2',
    date: new Date(2023, 4, 15),
    changes: [
      {
        type: 'fix',
        description: 'Fix a bug where an employee could reserve multiple ' +
          'desks for the same day'
      },
      {
        type: 'improved',
        description: 'Employee transition form improvements, including new ' +
          'computer fields'
      },
      {
        type: 'improved',
        description: 'Team calendar loading spinner'
      },
    ]
  },
  {
    version: '0.12.1',
    date: new Date(2023, 4, 5),
    changes: [
      {
        type: 'improved',
        description: 'Employee transition form improvements'
      },
    ]
  },
  {
    version: '0.12.0',
    date: new Date(2023, 4, 1),
    changes: [
      {
        type: 'new',
        description: 'Rebuild the Team App in Vue 3 for better performance ' +
          'and maintainability'
      },
    ]
  },
  {
    version: '0.11.0',
    date: new Date(2023, 2, 7),
    changes: [
      {
        type: 'new',
        description: 'Meals on Wheels module to track and manage delivery ' +
          'routes'
      },
      {
        type: 'improved',
        description: 'Do not require the Workflow Action urls be valid urls'
      },
    ]
  },
  {
    version: '0.10.0',
    date: new Date(2023, 1, 8),
    changes: [
      {
        type: 'new',
        description: 'Workflows module to facilitate and automate business ' +
          'processes'
      },
      {
        type: 'new',
        description: 'Employee onboarding workflow with staff transition form'
      },
    ]
  },
  {
    version: '0.9.0',
    date: new Date(2022, 11, 30),
    changes: [
      {
        type: 'new',
        description: 'Time Off approvers can set temporary approvers in their' +
          ' stead while they are on leave'
      },
      {
        type: 'improved',
        description: 'Various Time Off app improvements'
      },
    ]
  },
  {
    version: '0.8.8',
    date: new Date(2022, 11, 8),
    changes: [
      {
        type: 'improved',
        description: 'More security for desk reservation app'
      },
    ]
  },
  {
    version: '0.8.7',
    date: new Date(2022, 11, 8),
    changes: [
      {
        type: 'new',
        description: 'Add a Schaefers lobby kiosk landing page'
      },
    ]
  },
  {
    version: '0.8.6',
    date: new Date(2022, 10, 7),
    changes: [
      {
        type: 'improved',
        description: 'Block access to desk reservation pages for ' +
          'non-authenticated users unless they are on the LCOG network.'
      },
    ]
  },
  {
    version: '0.8.5',
    date: new Date(2022, 10, 3),
    changes: [
      {
        type: 'improved',
        description: 'Filter responsibilities by employee name.'
      },
      {
        type: 'improved',
        description: 'Responsibilities mobile views.'
      },
    ]
  },
  {
    version: '0.8.4',
    date: new Date(2022, 9, 25),
    changes: [
      {
        type: 'new',
        description: 'Manage email notification preferences on user profile ' +
          'screen.'
      },
      {
        type: 'improved',
        description: 'Calendar widget display improvements.'
      },
    ]
  },
  {
    version: '0.8.3',
    date: new Date(2022, 9, 24),
    changes: [
      {
        type: 'new',
        description: 'Daily help desk who is out emails.'
      },
    ]
  },
  {
    version: '0.8.2',
    date: new Date(2022, 9, 21),
    changes: [
      {
        type: 'improved',
        description: 'HTML email notifications.'
      },
    ]
  },
  {
    version: '0.8.1',
    date: new Date(2022, 8, 29),
    changes: [
      {
        type: 'fix',
        description: 'Fixed performance review print layout.'
      },
    ]
  },
  {
    version: '0.8.0',
    date: new Date(2022, 8, 23),
    changes: [
      {
        type: 'new',
        description: 'Add weekly time-off notifications for IS team.'
      },
      {
        type: 'new',
        description: 'Add time off request private notes visible only to ' +
          'manager.'
      },
    ]
  },
  {
    version: '0.7.1',
    date: new Date(2022, 7, 26),
    changes: [
      {
        type: 'new',
        description: 'Add profile edit page.'
      },
      {
        type: 'fix',
        description: 'Time off calendar now shows your whole team.'
      },
    ]
  },
  {
    version: '0.7.0',
    date: new Date(2022, 7, 24),
    changes: [
      {
        type: 'new',
        description: 'Add employee display name.'
      },
    ]
  },
  {
    version: '0.6.1',
    date: new Date(2022, 7, 22),
    changes: [
      {
        type: 'new',
        description: 'Update navigation.'
      },
    ]
  },
  {
    version: '0.6.0',
    date: new Date(2022, 7, 19),
    changes: [
      {
        type: 'new',
        description: 'Add employee numbers.'
      },
    ]
  },
  {
    version: '0.5.2',
    date: new Date(2022, 7, 12),
    changes: [
      {
        type: 'improved',
        description: 'Time off requests app improvments.'
      },
    ]
  },
  {
    version: '0.5.1',
    date: new Date(2022, 7, 10),
    changes: [
      {
        type: 'improved',
        description: 'Time off requests app improvments.'
      },
      {
        type: 'improved',
        description: 'Desk reservation app improvments.'
      },
    ]
  },
  {
    version: '0.5.0',
    date: new Date(2022, 7, 5),
    changes: [
      {
        type: 'new',
        description: 'Time off requests module: request, acknowledge, ' +
          'calendar, weekly report.'
      },
    ]
  },
  {
    version: '0.4.11',
    date: new Date(2022, 5, 28),
    changes: [
      {
        type: 'improved',
        description: 'Make desk numbers more readable in desk reservation app.'
      },
      {
        type: 'improved',
        description: 'Allow desk highlighting in desk reservation app.'
      }
    ]
  },
  {
    version: '0.4.10',
    date: new Date(2022, 5, 14),
    changes: [
      {
        type: 'improved',
        description: 'Allow for A/B desks in desk reservation app.'
      }
    ]
  },
  {
    version: '0.4.9',
    date: new Date(2022, 5, 8),
    changes: [
      {
        type: 'improved',
        description: 'Security upgrades.'
      }
    ]
  },
  {
    version: '0.4.8',
    date: new Date(2022, 4, 16),
    changes: [
      {
        type: 'improved',
        description: 'Add a screensaver at night to the desk reservation ' +
          'screens.'
      },
      {
        type: 'improved',
        description: 'Update Schaefers floor plans.'
      },
      {
        type: 'improved',
        description: 'Allow employees to be archived.'
      }
    ]
  },
  {
    version: '0.4.7',
    date: new Date(2022, 4, 9),
    changes: [
      {
        type: 'improved',
        description: 'Simplify desk reservation header.'
      }
    ]
  },
  {
    version: '0.4.6',
    date: new Date(2022, 4, 2),
    changes: [
      {
        type: 'new',
        description: 'Add a staging site for testing new features.'
      }
    ]
  },
  {
    version: '0.4.5',
    date: new Date(2022, 3, 30),
    changes: [
      {
        type: 'fix',
        description: 'Fix a bug where desks don\'t display on weekends.'
      }
    ]
  },
  {
    version: '0.4.4',
    date: new Date(2022, 3, 27),
    changes: [
      {
        type: 'improved',
        description: 'Desks can now have weekly holds placed on them for ' +
          'certain employees.'
      },
      {
        type: 'improved',
        description: 'Desk reservation app now blocked unless you are ' +
          'authenticated or on a trusted IP.'
      }
    ]
  },
  {
    version: '0.4.3',
    date: new Date(2022, 3, 22),
    changes: [
      {
        type: 'improved',
        description: 'Update floor plans processing code to be compatible ' +
          'with new Illustrator version changes.'
      },
      {
        type: 'improved',
        description: 'Desks can now be deactivated.'
      }
    ]
  },
  {
    version: '0.4.2',
    date: new Date(2022, 3, 19),
    changes: [
      {
        type: 'improved',
        description: 'Adjust desk reservation app to fit better on office ' +
          'laptop screens.'
      }
    ]
  },
  {
    version: '0.4.1',
    date: new Date(2022, 3, 18),
    changes: [
      {
        type: 'new',
        description: 'Add Desk Reservation reports.'
      },
      {
        type: 'improved',
        description: 'Responsibility app looks better on smaller screens.'
      }
    ]
  },
  {
    version: '0.4.0',
    date: new Date(2022, 3, 11),
    changes: [
      {
        type: 'improved',
        description: 'Migrate desk reservation data to a new Django app.'
      }
    ]
  },
  {
    version: '0.3.4',
    date: new Date(2022, 3, 8),
    changes: [
      {
        type: 'improved',
        description: 'End all active desk reservations every day at 7 PM.'
      }
    ]
  },
  {
    version: '0.3.3',
    date: new Date(2022, 3, 7),
    changes: [
      {
        type: 'improved',
        description: 'Add end time, rather than delete, desk reservations ' +
          'upon check out.'
      },
      {
        type: 'improved',
        description: 'Prevent double booking of desk reservations by ' +
          'canceling existing reservations when a new one is made.'
      }
    ]
  },
  {
    version: '0.3.2',
    date: new Date(2022, 2, 18),
    changes: [
      {
        type: 'improved',
        description: 'Added second and third Schaefers floors to desk ' +
          'reservation app'
      },
      {
        type: 'improved',
        description: 'Cleaned up desk reservation app layout'
      }
    ]
  },
  {
    version: '0.3.1',
    date: new Date(2022, 2, 9),
    changes: [
      {
        type: 'new',
        description: 'Responsibilities can be tagged'
      },
      {
        type: 'new',
        description: 'Responsibilities now have descriptions and links'
      },
      {
        type: 'new',
        description: 'View all responsibilities by tag'
      },
      {
        type: 'new',
        description: 'Filter all responsibility tables by name, description, ' +
          'and tag'
      },
      {
        type: 'improved',
        description: 'Responsibility app UI improvements'
      }
    ]
  },
  {
    version: '0.3.0',
    date: new Date(2022, 2, 7),
    changes: [
      {
        type: 'improved',
        description: 'Update desk reservation app UI significantly'
      },
      {
        type: 'improved',
        description: 'Migrate responsibility app data to its own Django app'
      }
    ]
  },
  {
    version: '0.2.2',
    date: new Date(2022, 1, 22),
    changes: [
      {
        type: 'new',
        description: 'Demo of mileage reimbursement app'
      }
    ]
  },
  {
    version: '0.2.1',
    date: new Date(2022, 1, 8),
    changes: [
      {
        type: 'new',
        description: 'Demo of desk reservation app'
      }
    ]
  },
  {
    version: '0.2.0',
    date: new Date(2022, 0, 14),
    changes: [
      {
        type: 'improved',
        description: 'Upgrade to Django 4'
      }
    ]
  },
  {
    version: '0.1.4',
    date: new Date(2021, 9, 29),
    changes: [
      {
        type: 'improved',
        description: 'Responsibilities module: filter employee list dropdown ' +
          'by typing'
      }
    ]
  },
  {
    version: '0.1.3',
    date: new Date(2021, 9, 26),
    changes: [
      {
        type: 'new',
        description: 'Responsibilities Module'
      },
      {
        type: 'new',
        description: 'Release Notes page'
      },
      {
        type: 'improved',
        description: 'Add LCOG logo to menu'
      },
      {
        type: 'improved',
        description: 'Add Schaefers 2nd and 3rd floor plans to seating chart'
      }
    ]
  },
  {
    version: '0.1.2',
    date: new Date(2021, 9, 11),
    changes: [
      {
        type: 'new',
        description: 'Seating chart demo'
      }
    ]
  },
  {
    version: '0.1.1',
    date: new Date(2021, 9, 7),
    changes: [
      {
        type: 'new',
        description: 'Add seating chart demo page'
      },
      {
        type: 'improved',
        description: 'Admin: Add user inline to group detail'
      }
    ]
  },
  {
    version: '0.1.0',
    date: new Date(2021, 9, 5),
    changes: [
      {
        type: 'new',
        description: 'Add app version to header'
      },
      {
        type: 'improved',
        description: 'Clean up navigation'
      }
    ]
  }
]
