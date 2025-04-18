# Testing network bandwidth with `iperf3`

`iperf3` is a command-line tool that tests the network connectivity between two hosts. It works by establishing a server on one host, to which another host can connect as a client. Normally it doesn't require special privileges to run on either side.

With `iperf3`, you don't need to worry about generating the data payload. It supports time-based and size-based payloads, as well as testing TCP vs. UDP, among other features.

# Installation

On both ends, install the utility.  
`sudo apt install iperf3`

# Firewall rules on server side

The server by default listens to the port 5201\. If there's firewall in place blocking the incoming connections, the port should be allowed.

First, figure out which network interface we are testing. The list of interfaces can be enumerated by  
`ip link show`  
And their associated IP addresses  
	`ip addr show`

If we already use ufw, we may allow incoming traffic on the interface, for example, by the command  
`sudo ufw allow in on [iface] from any to any comment 'bandwidth testing'`

This will allow all incoming traffic from everywhere to anything on the interface `[iface]`. The comment is for our convenience.

For more restrictive, port-based filtering, consider  
`sudo ufw allow in on [iface] from any to any port 5201`

This restricts the incoming traffic to the allowed port number.

# Starting `iperf3` server

`iperf3` doesn't really care which side we choose as the server. It is up to us to decide.

On the server side, start the application with  
`iperf3 -s`

It's possible to bind to the specific interface using the IP addresses associated with it.  
	`iperf3 -s -B [address]`  
This can help make sure we're testing the desired link just in case there's more than one being active.

# Running `iperf3` client

On the other host, to run iperf3 as client, use the command  
`iperf3 -c [address/hostname]`  
This will start the default TCP-based test that connects with the server identified by its address or hostname. Notice that if the server binds to a specific address, the address used in this command (or indirectly the address that the hostname resolves to) should match the server-bound address.

Normally we want to run the test for some extended time.  
`iperf3 -c [address/hostname] -t 300`  
This will run the test for 300 seconds.

By default, the client sends data to the server. This can be reversed by the `-R` switch on the commandline. It is often highly desirable to test bidirectional flow, which is enabled by the `--bidir` flag.

The default test is TCP based and uncapped. It figures out the "correct" bitrate by itself thanks to the TCP congestion-avoidance algorithm. To set a specific target of bitrate cap (because we know a certain link has a certain target speed), use the `-b` flag, for example, `-b 2.5G`.

Notice that TCP slow-start means that in the beginning of the test it is virtually certain that the full bandwidth of the link will *not* be utilized. This is not a problem with a sustained test but we may want to exclude the slow-start from the final average-speed reckoning by omitting the first *`N`* seconds with the options `-O N`.

In the case of UDP, the default bitrate is capped at `1Mbps`. This is not usually the correct target and should be adjusted manually.

Output information is displayed on both ends.