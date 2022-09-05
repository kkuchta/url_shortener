# Someone's automatically created a ton of urls (like hundreds of thousands).
# So now I need to clean them up.  This script will go through and delete any
# funtion older than a specific cutoff

require 'aws-sdk'
require 'pry-byebug'
require 'active_support'
require 'active_support/core_ext'

PAGE_SIZE = 10
CUT_OFF = 6.days
lambda = Aws::Lambda::Client.new(region: 'us-west-2', profile: 'apex')

count_deleted = 0
start = Time.now

total = lambda.get_account_settings.account_usage.function_count
puts "Total to delete: #{total}"
loop do
  begin
    lambda.list_functions(
      function_version: "ALL",
    ).each_page do |page|
      #if page.functions.count <= 0
        #puts "Got no functions for this page"
        #sleep 5
        #next
      #end
      page.functions.each do |function|
        # Shoulda used tags on these things.
        if function.function_name.match?(/^shortener_read_\d+$/) && function.last_modified < CUT_OFF.ago
          puts "delete #{function.function_name}"
          begin
            lambda.delete_function(function_name: function.function_name)
          rescue Aws::Lambda::Errors::ResourceNotFoundException => e
            puts "Got error #{e}"
          end
          count_deleted += 1
        else
          puts "skipping #{function.function_name}"
        end
      end
      elapsed_time = Time.now - start
      if count_deleted > 0
        time_per_item = elapsed_time / count_deleted
        puts "Average seconds to delete an item: #{time_per_item}"
        time_left_seconds = (total - count_deleted) * time_per_item
        puts "Estimated finish: #{time_left_seconds.seconds.from_now.strftime('%D %r')}"
      end
    end
  rescue Aws::Lambda::Errors::InvalidSignatureException => e
    puts "signature expired"
  end
end


puts 'done'
